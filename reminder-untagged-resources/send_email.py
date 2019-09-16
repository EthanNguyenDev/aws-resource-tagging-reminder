import boto3, json, os
from botocore.exceptions import ClientError
import requests

API_ENDPOINT_EMAIL = os.getenv('API_ENDPOINT_EMAIL') if os.getenv('API_ENDPOINT_EMAIL') else 'https://bclpfiib8f.execute-api.ap-southeast-1.amazonaws.com/prod/send'

def sendEmail(account_id, recipient_email, resource_list):
    req_body = {
        'account_id': account_id,
        'recipient_email': recipient_email,
        'resources': resource_list
    }
    return requests.post(API_ENDPOINT_EMAIL, data=json.dumps(req_body))
