"""
requirements.txt
# Function dependencies, for example:
# package>=version
google-cloud-core==0.29.1
google-cloud-storage==1.14.0
PyMySQL==0.9.3
requests==2.21.0
"""
import logging
from os import getenv
import pymysql
from pymysql.err import OperationalError
from google.cloud import storage
import requests

"""
Insert config.py variables here.
"""

CONNECTION_NAME = getenv("INSTANCE_CONNECTION_NAME", INSTANCE_CONNECTION_NAME)
DB_USER = getenv("MYSQL_USER", "root")
DB_PASSWORD = getenv("MYSQL_PASSWORD", MYSQL_DB_PASSWORD)
DB_NAME = getenv("MYSQL_DATABASE", MYSQL_DB_NAME)

mysql_config = {
    "user": DB_USER,
    "password": DB_PASSWORD,
    "db": DB_NAME,
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True,
}

# Create SQL connection globally to enable reuse
# PyMySQL does not include support for connection pooling
mysql_conn = None


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print("File {} uploaded to {}.".format(source_file_name, destination_blob_name))


def __get_cursor():
    """
    Helper function to get a cursor
      PyMySQL does NOT automatically reconnect,
      so we must reconnect explicitly using ping()
    """
    try:
        return mysql_conn.cursor()
    except OperationalError:
        mysql_conn.ping(reconnect=True)
        return mysql_conn.cursor()


def extract_pending_operations():
    global mysql_conn

    # Initialize connections lazily, in case SQL access isn't needed for this
    # GCF instance. Doing so minimizes the number of active SQL connections,
    # which helps keep your GCF instances under SQL connection limits.
    if not mysql_conn:
        try:
            mysql_conn = pymysql.connect(**mysql_config)
        except OperationalError:
            # If production settings fail, use local development ones
            mysql_config["unix_socket"] = f"/cloudsql/{CONNECTION_NAME}"
            mysql_conn = pymysql.connect(**mysql_config)

    # Remember to close SQL resources declared while running this function.
    # Keep any declared in global scope (e.g. mysql_conn) for later reuse.
    with __get_cursor() as cursor:
        cursor.execute(
            "SELECT filename, operationname FROM `OperationStatus` WHERE status = 'PROCESSING' AND operationname IS NOT NULL;"
        )
        results = cursor.fetchall()
        return results


def update_operation_status(operationname):
    global mysql_conn

    # Initialize connections lazily, in case SQL access isn't needed for this
    # GCF instance. Doing so minimizes the number of active SQL connections,
    # which helps keep your GCF instances under SQL connection limits.
    if not mysql_conn:
        try:
            mysql_conn = pymysql.connect(**mysql_config)
        except OperationalError:
            # If production settings fail, use local development ones
            mysql_config["unix_socket"] = f"/cloudsql/{CONNECTION_NAME}"
            mysql_conn = pymysql.connect(**mysql_config)

    # Remember to close SQL resources declared while running this function.
    # Keep any declared in global scope (e.g. mysql_conn) for later reuse.
    with __get_cursor() as cursor:
        sql = "UPDATE `OperationStatus` SET status = 'COMPLETED' WHERE operationname = %s;"
        cursor.execute(sql, (operationname))
        mysql_conn.commit()
        logging.info("Status updated successfully!")


def main_function(event, context):
    pendingOperations = extract_pending_operations()
    completedOperations = []

    for operation in pendingOperations:
        operationname = str(operation["operationname"])
        filename = operation["filename"]
        logging.info("Processing operation {}.".format(operationname))
        response = requests.get(
            "https://speech.googleapis.com/v1/operations/{}?key={}".format(
                operationname, GCP_API_KEY
            )
        ).json()
        if response["done"]:
            source_file_name = "{}.txt".format(filename[:-4])
            source_file_path = "/tmp/{}".format(source_file_name)
            with open(source_file_path, "w") as outputfile:
                for result in response["response"]["results"]:
                    # The first alternative is the most likely one for this portion.
                    outputfile.write(result["alternatives"][0]["transcript"])
            upload_blob(
                bucket_name=TRANSCRIPT_BUCKET_NAME,
                source_file_name=source_file_path,
                destination_blob_name=source_file_name,
            )
            logging.info("Operation {} uploaded successfully!".format(operationname))
            update_operation_status(operationname)
            logging.info("Entry {} updated.".format(operationname))

