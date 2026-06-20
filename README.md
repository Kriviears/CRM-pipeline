# CRM-pipeline

<ol>
<li>CRM message comes in via POST webhook invoke URL</li>
<ol>That API gateway method is hooked up to an event bridge which then calls a lambda function, webhook-fanout</ol>
<li> Webhook fanout grabs the important information out of the CRM event sent to it</li>
<ol>Stores the payload into an S3 bucket</ol>
<ol>Send the payload to an SQS queue</ol>
<li>After a 10 minute delay the delayed_process function is called
delayed_process reads the file at the address based on information in its payload
Then matches up specific information to be sent to an email or slack channel</li>
<li>Send-slack-message reads the message sent to it and through a slack app sends a message to any channel with that slack app in it</li>
</ol>
<br>
Thank you for reading
