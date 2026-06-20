# CRM-pipeline

Step 1: CRM message comes in via POST webhook invoke URL
that API gateway method is hooked up to an event bridge which then calls a lambda function, webhook-fanout
Step 2: Webhook fanout grabs the important information out of the CRM event sent to it
Stores the payload into an S3 bucket
Send the payload to an SQS queue
Step 3: After a 10 minute delay the delayed_process function is called
delayed_process reads the file at the address based on information in its payload
Then matches up specific information to be sent to an email or slack channel
Step 4: send-slack-message reads the message sent to it and through a slack app sends a message to any channel with that slack app in it

Thank you for reading
