# Audio-Transcriber-SPA
SPA built with Vue.js and Flask to transcribe audio to text

## Database
```
Download the proxy:
wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
Make the proxy executable: 
chmod +x cloud_sql_proxy
./cloud_sql_proxy -instances=<INSTANCE_CONNECTION_NAME>=tcp:3306


Enable Cloud SQL Admin API 
CREATE DATABASE transcribe_status;
USE transcribe_status;
CREATE TABLE status (entryID INT NOT NULL AUTO_INCREMENT, email VARCHAR(255), filename VARCHAR(255), transcriptionstatus VARCHAR(255), operationname VARCHAR(255), PRIMARY KEY(entryID));

INSERT INTO status (email, filename, status) values ("test@email.com", "audio-1231231.wav", "TRANSCRIBING");

```