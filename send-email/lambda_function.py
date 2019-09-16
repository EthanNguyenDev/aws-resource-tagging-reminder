import boto3, json
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    request_body = event.get('body')
    request_body = json.loads(request_body)
    ses_res = send_email(request_body.get('account_id'), request_body.get('recipient_email'), request_body.get('resources'))
    
    return {
        'statusCode': 200,
        'body': json.dumps(ses_res)
    }


def send_email(account_id, recipient_email, resource_list):
    SENDER = "AWS Team <XXX@gmail.com>"
    RECIPIENT = recipient_email
    TEMPLATE_NAME = "ResourceTaggingAlert"
    CC_ADDRESSES = [
        "YYY@gmail.com"
    ]
    CONFIGURATION_SET = "resource-tagging-alert-failure" #incase of SES failure, notify SNS topic (ops team subscribed)
    AWS_REGION = "us-east-1"
    client = boto3.client('ses',region_name=AWS_REGION)

    try:
        response = client.send_templated_email(
            Source=SENDER,
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
                'CcAddresses': CC_ADDRESSES,
            },
            Template=TEMPLATE_NAME,
            TemplateData=json.dumps({'account_id': account_id, 'recipient_email': recipient_email, 'resources': resource_list}),
            ConfigurationSetName=CONFIGURATION_SET,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        return response


# {
#     "account_id": "",
#     "recipient_email": "XXX@gmail.com",
#     "resources": [
#         {
#             "CreatedDate": "2019-09-10T10: 18: 48",
#             "CreatorArn": "arn:aws:sts: : ACCOUNT_ID:assumed-role/XXXXXXXX",
#             "EmailSent": false,
#             "EventId": "0ca7fce9-3404-5800-4dbf-c10a5b0bef03",
#             "ResourceKey": "arn:aws:kms:ap-southeast-1: ACCOUNT_ID:key/KEY_ID",
#             "ResourceMetadata": {},
#             "ResourceRegion": "ap-southeast-1",
#             "ResourceType": "kms",
#             "ShouldSentEmail": false
#         }
#     ]
# }