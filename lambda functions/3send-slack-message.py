
# Sends the slack message

import json
import os
import urllib3

logger_http = urllib3.PoolManager()

SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']


def lambda_handler(event, context):
    for record in event['Records']:
        # SQS message body
        sqs_body = json.loads(record['body'])

        # The actual payload published by the previous Lambda is wrapped in
        # the SNS "Message" field, itself a JSON string
        message = json.loads(sqs_body['Message'])

        send_to_slack(message)

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Processed all records'})
    }


def send_to_slack(message):
    """
    message is expected to look like:
    {
        "Name": "Emmaleigh Murray",
        "lead_id": "lead_bjKGXVqCHXjRcssJMASOGltiCSzcXsPrbb71donje8a",
        "Created Date": "2026-06-18T10:11:16.633000+00:00",
        "Label": "Potential",
        "Email": "someone@example.com",
        "Lead Owner": "Lucija Bitunjac",
        "Funnel": "DE ACADEMY Direct VSL"
    }
    """
    slack_payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🆕 New Lead Created"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Name:*\n{message.get('Name', 'N/A')}"},
                    {"type": "mrkdwn", "text": f"*Email:*\n{message.get('Email', 'N/A')}"},
                    {"type": "mrkdwn", "text": f"*Lead Owner:*\n{message.get('Lead Owner', 'N/A')}"},
                    {"type": "mrkdwn", "text": f"*Funnel:*\n{message.get('Funnel', 'N/A')}"},
                    {"type": "mrkdwn", "text": f"*Status:*\n{message.get('Label', 'N/A')}"},
                    {"type": "mrkdwn", "text": f"*Created:*\n{message.get('Created Date', 'N/A')}"}
                ]
            }
        ]
    }

    encoded_body = json.dumps(slack_payload).encode('utf-8')

    response = logger_http.request(
        'POST',
        SLACK_WEBHOOK_URL,
        body=encoded_body,
        headers={'Content-Type': 'application/json'}
    )

    if response.status != 200:
        raise Exception(
            f"Slack webhook returned status {response.status}: {response.data.decode('utf-8')}"
        )

    return response.status