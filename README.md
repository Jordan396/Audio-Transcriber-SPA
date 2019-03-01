# Audio-Transcriber-SPA
## Overview
[https://thebackyardmoose.com/audio-transcriber](https://thebackyardmoose.com/audio-transcriber)

Audio transcription can be an extremely tedious process - I know, I've been there. Hence, I designed this single page web application to provide my friends and myself with a quick and easy way to convert audio to text. Once the conversion process completes, users are automatically emailed their transcripts (note that emails may be marked as *Spam*).

Currently, the application only supports *.wav* files not exceeding *16MB*.

**IMPORTANT:** As much as possible, I strive to keep this application *free of charge*. However, this is only possible with your support. If you'd like to contribute, become a Patreon at [*TheBackyardMoose*](https://www.patreon.com/TheBackyardMoose).

---

## Tools and Workflow
![](img/flowchart.png)

1. User enters email and uploads audio file to *Vue.js* frontend.
2. Once the user clicks submit, a POST request is sent to the *Flask API* backend.
3. The Flask backend:
   1. Inserts user's email address into MySQL database.
   2. Uploads user's audio file to Google Cloud Storage.
4. Once audio file upload is complete, Google Cloud Storage trigger fires off cloud function 1.
5. Cloud function 1 starts the conversion process using Google Speech-to-Text API. This ID of the operation created is stored in the database.
6. Cloud function 2 sends a GET request to the Speech-to-Text API periodically, for all pending operations. Once an operation is deemed complete, the text in the HTTP response is saved into a file and uploaded to Google Cloud Storage.
7. Cloud function 3:
   1. Once text file upload is complete, Google Cloud Storage trigger fires off cloud function 3.
   2. Cloud function also queries the database to extract user's email address.
8. An email directed at the user's email address along with a signedUrl link to the transcript text file is created. This email is passed along to the SendGrid API.
9. The SendGrid API sends the email to the user.

## Installation
As I'm really busy with school, I'll only be posting partial installation instructions. If you're keen on setting up the application for yourself, send me an email at jordan.chyehong@gmail.com. I'll release further instructions accordingly! :)

### Database Management (Linux)
#### Setting up proxy for external connections
1. Make the proxy executable 
```
chmod +x cloud_sql_proxy
```
2. Start the connection
```
./cloud_sql_proxy -instances=<INSTANCE_CONNECTION_NAME>=tcp:3306 -credential_file=<PATH_TO_KEY_FILE> &
```

#### Creating tables
Navigate to *Cloud SQL* in GCP. Create a new database instance and then click *Connect using Cloud Shell*. Enter the following commands:
1. Create the Database. 
```
CREATE DATABASE operation_status;
```
2. Use the Database. 
```
USE operation_status;
```
3. Create the *OperationStatus* table
```
CREATE TABLE OperationStatus (entryID INT NOT NULL AUTO_INCREMENT, email VARCHAR(255), filename VARCHAR(255), status VARCHAR(255), operationname VARCHAR(255), PRIMARY KEY(entryID));
```

