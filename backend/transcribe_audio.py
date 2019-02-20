"""
requirements.txt
# Function dependencies, for example:
# package>=version
google-cloud-core==0.29.1
google-cloud-speech==0.36.3
google-cloud-storage==1.14.0
PyMySQL==0.9.3
"""
import logging
from os import getenv

import pymysql
from pymysql.err import OperationalError

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

MYSQL_DB_PASSWORD = config.MYSQL_DB_PASSWORD
INSTANCE_CONNECTION_NAME = config.INSTANCE_CONNECTION_NAME
AUDIO_BUCKET_NAME = config.AUDIO_BUCKET_NAME

CONNECTION_NAME = getenv("INSTANCE_CONNECTION_NAME", INSTANCE_CONNECTION_NAME)
DB_USER = getenv("MYSQL_USER", "root")
DB_PASSWORD = getenv("MYSQL_PASSWORD", MYSQL_DB_PASSWORD)
DB_NAME = getenv("MYSQL_DATABASE", "transcribe_status")

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


def mysql_demo(operationname, filename):
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
        try:
            sql = "UPDATE `status` SET operationname = %s WHERE filename = %s;"
            cursor.execute(sql, (operationname, filename))
            mysql_conn.commit()
            logging.info("Status updated successfully!")
        finally:
            mysql_conn.close()


def transcribe_audio(event, context):
    """
    Asynchronously transcribes the audio file specified by the gcs_uri.
    Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    client = speech.SpeechClient()
    filename = format(event["name"])
    uri = "gs://{}/{}".format(AUDIO_BUCKET_NAME,filename)
    logging.info("Resource URI: ".format(uri))
    audio = types.RecognitionAudio(uri=uri)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16, language_code="en-US"
    )
    operation = client.long_running_recognize(config, audio)
    operationname = operation.operation["Operation name"]
    logging.info("Operation {} completed.".format(operationname))
    mysql_demo(operationname=operationname, filename=filename)
