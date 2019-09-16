import boto3
import re, os, datetime, logging
from util import *

def lambda_handler(event, context):
    user_arn = event.get('detail').get('userIdentity').get('arn')
    # ignore event caused by certain user like pipeline|autoscaling
    if is_created_by_pipeline(user_arn):
        return

    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
    table = dynamodb.Table('CloudTrailEventResourceTracking')
    try:
        response = table.put_item(Item=prepareDbItem(event))
        print("PutItem succeeded")
    except Exception as e:
        logging.warning("Exception: {}".format(e))

def prepareDbItem(event):
    return {
        'EventId': event.get('id'),
        'CreatorArn': event.get('detail').get('userIdentity').get('arn'),
        'ResourceKey': derive_resource_key(event),
        #'ResourceArn': derive_resource_arn(event), #DynamoDB not allow emptry string
        'ResourceType': derive_resource_type(event),
        'ResourceRegion': event.get('detail').get('awsRegion'),
        'ResourceMetadata': {},
        'EmailSent': False,
        'ShouldSendEmail': True,
        'CreatedDate': datetime.datetime.now().replace(microsecond=0).isoformat(), #sg localtime
    }

