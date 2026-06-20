

# This function grabs the relevant information from the CRM event, stores it in the S3 for archiving and 
# passes on that information to the sqs

import json
import boto3

import datetime

s3 = boto3.client('s3')
sqs = boto3.client('sqs')

BUCKET = 'crm-webhook-config'
PREFIX = 'webhooks/subscribers/'
EVENT_LOG_PREFIX = 'webhooks/events/'
DELAY_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/627330319849/webhook-delay'



def lambda_handler(event, context):
    print(f"Full event: {json.dumps(event)}")

    detail = event.get('detail', {})
    event_type = detail.get('eventType')
    payload = event.get('detail', {})

    print(f"Event type: {event_type}")
    print(f"Payload: {payload}")
    print(f"Detail: {json.dumps(detail)}")

    # Load subscriber configs from S3
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=PREFIX)
    subscribers = []
    for obj in response.get('Contents', []):
        print(f"Found key: {obj['Key']}")
        if obj['Key'].endswith('/'):
            continue
        file = s3.get_object(Bucket=BUCKET, Key=obj['Key'])
        sub = json.loads(file['Body'].read())
        subscribers.append(sub)

    # Log the incoming event to its own prefix (NOT the subscribers prefix,
    # otherwise the loop above will try to parse these as subscriber configs)
    lead_id = payload.get('event', {}).get('lead_id', 'unknown')
    log_key = f'{EVENT_LOG_PREFIX}crm_event_{lead_id}.json'
    s3.put_object(
        Bucket=BUCKET,
        Key=log_key,
        Body=json.dumps({
            "payload": payload,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }),
        ContentType='application/json'
    )

    # Send to delay queue for downstream processing 10 minutes later
    sqs.send_message(
        QueueUrl=DELAY_QUEUE_URL,
        MessageBody=json.dumps({
            "eventType": event_type,
            "payload": detail
        })
    )