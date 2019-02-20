from flask import Flask, render_template, redirect, request, jsonify, url_for
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import datetime
import config
import pymysql
from google.cloud import storage

AUDIO_BUCKET_NAME = config.AUDIO_BUCKET_NAME
MYSQL_DB_PASSWORD = config.MYSQL_DB_PASSWORD
UPLOAD_FOLDER = "./media/uploads"
ALLOWED_EXTENSIONS = set(["wav"])

app = Flask(__name__, static_folder="./dist/static", template_folder="./dist")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route("/<path:path>")
def catch_all(path):
    return render_template("index.html")


@app.route("/api/transcribe-audio", methods=["POST"])
def transcribeAudio():
    print(os.getcwd())
    user_email = request.form["user-email"]
    # check if the post request has the file part
    if "file" not in request.files:
        print("No file part")
        return render_template("index.html")
    file = request.files["file"]
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == "":
        print("No selected file")
        return render_template("index.html")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        source_file_name = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        # Get current time for file identification
        now = datetime.datetime.now()
        timeIdentifier = now.strftime("%Y%m%d%H%M")
        gcp_filename = "audio-{}.wav".format(timeIdentifier)
        destination_blob_name = "audio/{}".format(gcp_filename)
        file.save(source_file_name)
        upload_blob(AUDIO_BUCKET_NAME, source_file_name, destination_blob_name)
        insert_into_db(mysql_db_password=MYSQL_DB_PASSWORD, user_email=user_email, gcp_filename=gcp_filename)
    else:
        print("File not allowed!")
    return render_template("index.html")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print("File {} uploaded to {}.".format(source_file_name, destination_blob_name))


def insert_into_db(mysql_db_password, user_email, gcp_filename):
    connection = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password=mysql_db_password,
        db="transcribe_status",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `status` (`email`, `filename`, `transcriptionstatus`) VALUES (%s, %s, %s)"
            cursor.execute(
                sql, (user_email, gcp_filename, "TRANSCRIBING")
            )

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()
    finally:
        connection.close()
