import re, os, datetime, logging, json
import boto3, botocore
from send_email import sendEmail
from util import *

def lambda_handler(event, context):
    table = get_dynamo_db_table()
    response = table.scan()
    
    items = response.get('Items')
    untagged_items = []
    email_sent_items = []

    for item in items:
        resource_key = item.get('ResourceKey')
        resource_arn = item.get('ResourceArn')
        resource_type = item.get('ResourceType')
        #resource_region = item.get('ResourceRegion') if item.get('ResourceRegion') else 'ap-southeast-1'
        if isBlank(resource_arn):
            resource_arn = look_up_arn_from_key(db_item=item, resource_type=resource_type, resource_key=resource_key)

        valid = is_resource_properly_tagged(db_item=item, resource_type=resource_type, resource_key=resource_key, resource_arn=resource_arn)
        #print("resource key {}  is properly tagged? {}".format(resource_type + ':' + resource_key , bool(valid)))
        if not valid and item.get('ShouldSendEmail'):
            untagged_items.append(item)

    untagged_items_by_creator = list(map(lambda item: 
        {
            "creator_email": item.get('CreatorArn').rsplit('/',1)[1] + '@gmail.com',
            'resources': list(filter(lambda original_item: item.get('CreatorArn') == original_item.get('CreatorArn'), untagged_items))
        }
    , untagged_items))

    untagged_items_by_creator = remove_duplicate_records_by_creator(untagged_items_by_creator)
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    for item in untagged_items_by_creator:
        response = sendEmail(account_id=account_id, recipient_email=item.get('creator_email'), resource_list=item.get('resources'))
        if response.status_code == 200:
            for item in item.get('resources'):
                email_sent_items.append({
                    "ResourceKey": item.get('ResourceKey'),
                    "ResourceType": item.get('ResourceType')
                })

    for item in email_sent_items:
        table.update_item(
            Key={
                "ResourceKey": item.get('ResourceKey'),
                "ResourceType": item.get('ResourceType')
            },
            UpdateExpression='SET #attr = :val',
            ExpressionAttributeNames={'#attr': 'EmailSent'},
            ExpressionAttributeValues={':val': 'true' }
        )

def look_up_arn_from_key(db_item, resource_key, resource_type):
    resource_region = db_item.get('ResourceRegion') if db_item.get('ResourceRegion') else 'ap-southeast-1'
    try:
        if resource_type == 'kinesis':
            #kinensi works by stream name, resourceArn not required
            return ''

        elif resource_type == 'dynamodb':
            dynamodb = boto3.client('dynamodb')
            response = dynamodb.describe_table(TableName=resource_key)
            return response.get('Table').get('TableArn')

        elif resource_type == 'rds':
            rds = boto3.client('rds')
            response = rds.describe_db_instances(DBInstanceIdentifier=resource_key)
            return response.get('DBInstances')[0].get('DBInstanceArn')

        elif resource_type == 'elasticloadbalancing':
            elasticloadbalancing = boto3.client('elbv2')
            response = elasticloadbalancing.describe_load_balancers(Names=[resource_key])
            return response.get('LoadBalancers')[0].get('LoadBalancerArn')

        elif resource_type == 'apigateway':
            # iterate thru all API stages to check tag, cannot check tag at API level, resourceArn not required
            return ''
        elif resource_type == 'lambda':
            # tags can be retrieved from get_function(FunctionName), resourceArn not required
            return ''
        elif resource_type == 'redshift':
            # tags can be retrieved from describe_clusters(ClusterIdentifier), resourceArn not required
            return ''
        elif resource_type == 's3':
            # tags can be retrieved from get_bucket_tagging(Bucket), resourceArn not required
            return ''
        elif resource_type == 'es':
            es = boto3.client('es')
            response = es.describe_elasticsearch_domain(DomainName=resource_key)
            return response.get('DomainStatus').get('ARN')
        elif resource_type == 'elasticache':
            account_id = boto3.client('sts').get_caller_identity().get('Account')
            return 'arn:aws:elasticache:' + resource_region + ':' + account_id + ':cluster:' + resource_key
        elif resource_type == 'kms':
            # arn is already save in DynamoDB as it's part of responseElement
            return resource_key

    except botocore.exceptions.ClientError as err:
        handle_error(db_item=db_item, err=err)

def is_resource_properly_tagged(db_item, resource_type, resource_key, resource_arn):
    if resource_arn is None:
        logging.warning("Resouces {} not found, proceed to delete equivalent event in DynamoDB".format(db_item.get('ResourceKey')))
        delete_dynamo_db_item(db_item)
        return True
    try:
        if resource_type == 'kinesis':
            kinesis = boto3.client('kinesis')
            response = kinesis.list_tags_for_stream(StreamName=resource_key, Limit=50)
            return is_tag_list_contain_valid_pc_code(response.get('Tags'))

        elif resource_type == 'dynamodb':
            dynamodb = boto3.client('dynamodb')
            response = dynamodb.list_tags_of_resource(ResourceArn=resource_arn)
            return is_tag_list_contain_valid_pc_code(response.get('Tags'))

        elif resource_type == 'rds':
            rds = boto3.client('rds')
            response = rds.list_tags_for_resource(ResourceName=resource_arn)
            return is_tag_list_contain_valid_pc_code(response.get('TagList'))

        elif resource_type == 'elasticloadbalancing':
            elasticloadbalancing = boto3.client('elbv2')
            response = elasticloadbalancing.describe_tags(ResourceArns=[resource_arn])
            return is_tag_list_contain_valid_pc_code(response.get('TagDescriptions')[0].get('Tags'))

        elif resource_type == 'apigateway':
            apigateway = boto3.client('apigateway')
            stages = apigateway.get_stages(restApiId=resource_key.split('-')[-1])

            items = stages.get('Items')
            valid = True
            for item in items or []:
                valid = is_tag_dict_contain_valid_pc_code(item.get('Tags'))
            return valid

        elif resource_type == 'lambda':
            lamb = boto3.client('lambda')
            response = lamb.get_function(FunctionName=resource_key)
            return is_tag_dict_contain_valid_pc_code(response.get('Tags'))

        elif resource_type == 'redshift':
            redshift = boto3.client('redshift')
            response = redshift.describe_clusters(ClusterIdentifier=resource_key)
            return is_tag_list_contain_valid_pc_code(response.get('Clusters')[0].get('Tags'))

        elif resource_type == 's3':
            s3 = boto3.client('s3')
            response = s3.get_bucket_tagging(Bucket=resource_key)
            return is_tag_list_contain_valid_pc_code(response.get('TagSet'))

        elif resource_type == 'es':
            es = boto3.client('es')
            response = es.list_tags(ARN=resource_arn)
            return is_tag_list_contain_valid_pc_code(response.get('TagList'))

        elif resource_type == 'elasticache':
            elasticache = boto3.client('elasticache')
            response = elasticache.list_tags_for_resource(ResourceName=resource_arn)
            return is_tag_list_contain_valid_pc_code(response.get('TagList'))
        
        elif resource_type == 'kms':
            kms = boto3.client('kms')
            response = kms.list_resource_tags(KeyId=resource_arn)
            return is_tag_list_contain_valid_pc_code(response.get('Tags'))
        else:
            raise Exception('Invalid resource type {}'.format(resource_type))
        
        return False
    except botocore.exceptions.ClientError as err:
        handle_error(db_item=db_item, err=err)
        return True

def get_dynamo_db_table():
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
    table = dynamodb.Table('CloudTrailEventResourceTracking')
    return table

def delete_dynamo_db_item(db_item):
    table = get_dynamo_db_table()
    table.delete_item(
        Key={
            'EventId': db_item.get('EventId'),
            'CreatorArn': db_item.get('CreatorArn')
        }
    )

def remove_duplicate_records_by_creator(list_creator):
    set_of_jsons = { json.dumps(d, sort_keys=True) for d in list_creator}
    return [json.loads(t) for t in set_of_jsons]

def handle_error(db_item, err):
    status = err.response["ResponseMetadata"]["HTTPStatusCode"]
    errcode = err.response["Error"]["Code"]
    if status == 404 or errcode == 'ResourceNotFoundException':
        delete_dynamo_db_item(db_item)
        logging.warning("ResourceNotFoundException, Resouces {} may have been deleted, thus deleted equivalent event in DynamoDB".format(db_item.get('ResourceKey')))
    elif status == 403:
        logging.error("----------------Access denied, %s", err.response["Error"])
    else:
        logging.exception("----------------Error in request, %s", err.response["Error"])
