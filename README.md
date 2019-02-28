# Audio-Transcriber-SPA
SPA built with Vue.js and Flask to transcribe audio to text

## Database Management (Linux)
### Setting up proxy for external connections
1. Make the proxy executable 
```
chmod +x cloud_sql_proxy
```
2. Start the connection
```
./cloud_sql_proxy -instances=<INSTANCE_CONNECTION_NAME>=tcp:3306 -credential_file=<PATH_TO_KEY_FILE> &
```

### Creating tables
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

