
# Finds the appropriate file in the dea-lead-owner bucket
# Creates the object that the new lead message needs to create the slack message
import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

PUBLIC_BUCKET = "dea-lead-owner"
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:627330319849:new-lead-message.fifo"

def lambda_handler(event, context):
    logger.info(f'Full event {json.dumps(event)}')

    # SQS wraps each message in event['Records']; the actual payload
    # sent via sqs.send_message is a JSON string in record['body']
    results = []
    for record in event['Records']:
        body = json.loads(record['body'])
        results.append(process_lead(body))

    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }


def process_lead(body):
    event_data = body['payload']['event']
    lead_id = event_data['lead_id']
    data = event_data['data']

    file_key = f'{lead_id}.json'
    public_url = f"https://{PUBLIC_BUCKET}.s3.us-east-1.amazonaws.com/{file_key}"

    try:
        s3_client = boto3.client('s3')
        response = s3_client.get_object(
            Bucket=PUBLIC_BUCKET,
            Key=file_key
        )
        file_content_str = response['Body'].read().decode('utf-8')
        logger.info(f'Successfully read content from {file_key}. Content length: {len(file_content_str)}')

        # parse the JSON string into a dict so we can access fields
        file_content = json.loads(file_content_str)

        message = {
            'Name': data['display_name'],
            'lead_id': lead_id,
            'Created Date': data['date_created'],
            'Label': data['status_label'],
            'Email': file_content['lead_email'],
            'Lead Owner': file_content['lead_owner'],
            'Funnel': file_content['funnel']
        }

        # Publish to SNS
        sns_client = boto3.client('sns')
        sns_response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(message),
            Subject='New Lead Created',
            MessageGroupId='new-lead'
        )
        logger.info(f"Lead published to SNS: {sns_response['MessageId']}")

        return {
            'message': 'File read successfully',
            'url': public_url,
            'content': file_content
        }

    except Exception as e:
        logger.error(f'Error reading file {file_key}: {str(e)}')
        return {
            'bucket': PUBLIC_BUCKET,
            'file_key': file_key,
            'error': str(e),
            'status': 'error'
        }