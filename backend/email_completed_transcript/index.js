'use strict';

// [START functions_sendgrid_setup]
const sendgrid = require('sendgrid');
const mysql = require('mysql');

// Get a reference to the Cloud Storage component
const { Storage } = require('@google-cloud/storage');
const storage = new Storage();
// [END functions_sendgrid_setup]

// [START main_function]
/**
 * Cloud Function triggered by Cloud Storage when a file is uploaded.
 *
 * @param {object} event The Cloud Functions event.
 * @param {object} event.data A Cloud Storage file object.
 * @param {string} event.data.bucket Name of the Cloud Storage bucket.
 * @param {string} event.data.name Name of the file.
 * @param {string} [event.data.timeDeleted] Time the file was deleted if this is a deletion event.
 * @see https://cloud.google.com/storage/docs/json_api/v1/objects#resource
 */
exports.main_function = (event, callback) => {
    const file = event;

    /*
     TODO: INSERT CONFIG VARS HERE
    */

    extractEmailFromDB(file, MYSQL_CONFIG, SENDGRID_KEY, remainingFunction);

};
// [END main_function]

// [START functions_sendgrid_get_client]
/**
 * Returns a configured SendGrid client.
 *
 * @param {string} key Your SendGrid API key.
 * @returns {object} SendGrid client.
 */
function getClient(key) {
    if (!key) {
        const error = new Error(
            'SendGrid API key not provided. Make sure you have a "sg_key" property in your request querystring'
        );
        error.code = 401;
        throw error;
    }

    // Using SendGrid's Node.js Library https://github.com/sendgrid/sendgrid-nodejs
    return sendgrid(key);
}
// [END functions_sendgrid_get_client]

// [START functions_get_payload]
/**
 * Constructs the SendGrid email request from the HTTP request body.
 *
 * @param {object} requestBody Cloud Function request body.
 * @param {string} data.to Email address of the recipient.
 * @param {string} data.from Email address of the sender.
 * @param {string} data.subject Email subject line.
 * @param {string} data.body Body of the email subject line.
 * @returns {object} Payload object.
 */
function getPayload(requestBody) {
    if (!requestBody.to) {
        const error = new Error(
            'To email address not provided. Make sure you have a "to" property in your request'
        );
        error.code = 400;
        throw error;
    } else if (!requestBody.from) {
        const error = new Error(
            'From email address not provided. Make sure you have a "from" property in your request'
        );
        error.code = 400;
        throw error;
    } else if (!requestBody.subject) {
        const error = new Error(
            'Email subject line not provided. Make sure you have a "subject" property in your request'
        );
        error.code = 400;
        throw error;
    } else if (!requestBody.body) {
        const error = new Error(
            'Email content not provided. Make sure you have a "body" property in your request'
        );
        error.code = 400;
        throw error;
    }

    return {
        personalizations: [
            {
                to: [
                    {
                        email: requestBody.to,
                    },
                ],
                subject: requestBody.subject,
            },
        ],
        from: {
            email: requestBody.from,
        },
        content: [
            {
                type: 'text/plain',
                value: requestBody.body,
            },
        ],
    };
}
// [END functions_get_payload]

// [START functions_sendgrid_email]
/**
 * Send an email using SendGrid.
 *
 * Trigger this function by making a POST request with a payload to:
 * https://[YOUR_REGION].[YOUR_PROJECT_ID].cloudfunctions.net/sendEmail?sg_key=[YOUR_API_KEY]
 *
 * @example
 * curl -X POST "https://us-central1.your-project-id.cloudfunctions.net/sendEmail?sg_key=your_api_key" --data '{"to":"bob@email.com","from":"alice@email.com","subject":"Hello from Sendgrid!","body":"Hello World!"}' --header "Content-Type: application/json"
 *
 * @param {object} req Cloud Function request context.
 * @param {object} req.query The parsed querystring.
 * @param {string} req.query.sg_key Your SendGrid API key.
 * @param {object} req.body The request payload.
 * @param {string} req.body.to Email address of the recipient.
 * @param {string} req.body.from Email address of the sender.
 * @param {string} req.body.subject Email subject line.
 * @param {string} req.body.body Body of the email subject line.
 * @param {object} res Cloud Function response context.
 */
function sendgridEmail(req) {
    return Promise.resolve()
        .then(() => {
            if (req.method !== 'POST') {
                const error = new Error('Only POST requests are accepted');
                error.code = 405;
                throw error;
            }

            // Get a SendGrid client
            const client = getClient(req.sendgridKey);

            // Build the SendGrid request to send email
            const request = client.emptyRequest({
                method: 'POST',
                path: '/v3/mail/send',
                body: getPayload(req.body),
            });

            // Make the request to SendGrid's API
            console.log(`Sending email to: ${req.body.to}`);
            return client.API(request);
        })
        .catch(err => {
            console.error(err);
            return Promise.reject(err);
        });
};
// [END functions_sendgrid_email]
async function extractEmailFromDB(file, MYSQL_CONFIG, SENDGRID_KEY, callback) {
    const connectionName =
        process.env.INSTANCE_CONNECTION_NAME || MYSQL_CONFIG.INSTANCE_CONNECTION_NAME;
    const dbUser = process.env.SQL_USER || MYSQL_CONFIG.MYSQL_DB_USERNAME;
    const dbPassword = process.env.SQL_PASSWORD || MYSQL_CONFIG.MYSQL_DB_PASSWORD;
    const dbName = process.env.SQL_NAME || MYSQL_CONFIG.MYSQL_DB_NAME;

    const mysqlConfig = {
        connectionLimit: 1,
        user: dbUser,
        password: dbPassword,
        database: dbName,
    };
    if (process.env.NODE_ENV === 'production') {
        mysqlConfig.socketPath = `/cloudsql/${connectionName}`;
    }

    // Connection pools reuse connections between invocations,
    // and handle dropped or expired connections automatically.
    let mysqlPool;


    // Initialize the pool lazily, in case SQL access isn't needed for this
    // GCF instance. Doing so minimizes the number of active SQL connections,
    // which helps keep your GCF instances under SQL connection limits.
    if (!mysqlPool) {
        mysqlPool = mysql.createPool(mysqlConfig);
    }
    const fileIdentifier = file.name.slice(0, -4) + ".wav";
    console.log(fileIdentifier);
    const queryString = `SELECT email FROM OperationStatus WHERE filename="${fileIdentifier}";`;
    console.log(queryString);

    let queryResults = mysqlPool.query(queryString, (err, results) => {
        if (err) {
            console.log("ERROR HERE");
            return reject(err);
        } else {
            console.log(JSON.stringify(results));
            callback(file, results[0].email, SENDGRID_KEY);
        }
    });
    // Close any SQL resources that were declared inside this function.
    // Keep any declared in global scope (e.g. mysqlPool) for later reuse.
}

function remainingFunction(file, receipientEmail, SENDGRID_KEY) {
    return Promise.resolve()
        .then(() => {
            if (!file.bucket) {
                throw new Error(
                    'Bucket not provided. Make sure you have a "bucket" property in your request'
                );
            } else if (!file.name) {
                throw new Error(
                    'Filename not provided. Make sure you have a "name" property in your request'
                );
            }
        })
        .then(() => {
            const options = {
                action: 'read',
                expires: '03-17-2025',
            };

            const signedUrl = storage.bucket(file.bucket)
                .file(file.name)
                .getSignedUrl(options)
                .then(results => {
                    const urlString = results[0];
                    console.log(`The signed url for ${file.name} is ${urlString}.`);
                    return urlString;
                });
            return signedUrl;
        })
        .then((signedUrl) => {
            const emailBody = "Greetings!\n\n" +
                "You may access your transcript here:\n\n" +
                signedUrl +
                "\n\nIf you'd like to lend your support, visit:\n\n" +
                "https://www.patreon.com/TheBackyardMoose\n\n" +
                "Warm regards,\n\n" +
                "TheBackyardMoose";
            const req = {
                sendgridKey: SENDGRID_KEY,
                method: "POST",
                body: {
                    to: receipientEmail,
                    from: "jordan.chyehong@gmail.com",
                    subject: "Your transcript is ready!",
                    body: emailBody
                }
            };

            if (file.resourceState === 'not_exists') {
                // This was a deletion event, we don't want to process this
                return;
            }
            sendgridEmail(req);
        })
        .catch(err => {
            console.log("Job failed!");
            return Promise.reject(err); W
        });
}