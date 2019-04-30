# -*- coding: utf-8 -*-
"""Main file to be executed.

This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.

Example:
    Running the application.

        $ (venv) FLASK_APP=run.py FLASK_DEBUG=1 flask run

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

 @author: Jordan396 <https://github.com/Jordan396/Trivial-Twitter-Sockets>
                                                                                                                               
You should have received a copy of the MIT License when cloning this   
repository. If not, see <https://opensource.org/licenses/MIT>.         
"""

import os
import datetime
import pymysql
import ast
import json
from flask import Flask, render_template, redirect, request, jsonify, url_for
from werkzeug.utils import secure_filename
from flask_cors import CORS
from google.cloud import storage

__author__ = "Jordan396"
__copyright__ = "Copyright 2019, Jordan396"
__credits__ = ["Jordan396"]
__license__ = "MIT"
__maintainer__ = "Jordan396"
__email__ = "jordan.chyehong@gmail.com"
__status__ = "Debug"

AUDIO_BUCKET_NAME = "audio-transcriber-recordings"
UPLOAD_FOLDER = "/tmp"
ALLOWED_EXTENSIONS = set(["wav"])

app = Flask(__name__, static_folder="./dist/static", template_folder="./dist")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

with open('tmp/gsa.json', 'w') as outfile:
    json.dump(ast.literal_eval(os.environ.get(
        'GOOGLE_SERVICE_ACCOUNT')), outfile)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "tmp/gsa.json"


@app.route("/<path:path>")
def catch_all(path):
    return render_template("index.html")


@app.route("/api/transcribe-audio", methods=["POST"])
def transcribeAudio():
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
        gcp_filename = "{}|audio{}.wav".format(user_email, timeIdentifier)
        file.save(source_file_name)
        upload_blob(AUDIO_BUCKET_NAME, source_file_name, gcp_filename)
    else:
        print("File not allowed!")
    return render_template("index.html")


def allowed_file(filename):
    hasValidExtension = "." in filename and filename.rsplit(
        ".", 1)[1].lower() in ALLOWED_EXTENSIONS
    hasValidFilename = "|" not in filename
    return (hasValidExtension and hasValidFilename)


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print("File {} uploaded to {}.".format(
        source_file_name, destination_blob_name))


if __name__ == "__main__":
    app.run(host='0.0.0.0')
