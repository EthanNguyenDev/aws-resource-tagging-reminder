import os, re

DELIMITER = os.getenv('USER_DELIMITER') if os.getenv('USER_DELIMITER') else ','
EXCLUDED_USER_LIST = os.getenv('USER_LIST').split(DELIMITER) if os.getenv('USER_LIST') else ['pipeline']
PC_CODE_TAG_NAME = os.getenv('PC_CODE_TAG_NAME') if os.getenv('PC_CODE_TAG_NAME') else 'PC-code'

def isBlank (myString):
    if myString and myString.strip():
        #myString is not None AND myString is not empty or blank
        return False
    #myString is None OR myString is empty or blank
    return True

def is_created_by_pipeline(arn):
    if arn:
        userId = arn.rsplit('/',1)[1]
        found = [username for username in EXCLUDED_USER_LIST if userId == username]
        return len(found) > 0
    # kill anyway if not found identity in arn
    return False

def is_valid_pc_code(pc_code):
    pattern = re.compile("^[A-Za-z0-9]{4}$")
    return pattern.match(pc_code)

def is_tag_dict_contain_valid_pc_code(tag_dict):
    if tag_dict is not None:
        return is_valid_pc_code(tag_dict.get(PC_CODE_TAG_NAME))
    return False

def is_tag_list_contain_valid_pc_code(tags):
    for tag in tags:
        if PC_CODE_TAG_NAME  == tag.get('Key') or PC_CODE_TAG_NAME == tag.get('key'):
            pc_code = tag.get('value') if tag.get('value') else tag.get('Value') 
            return is_valid_pc_code(pc_code)
    return False

def derive_resource_key(event):
    event_source = event.get('source')
    detail = event.get('detail')
    request_parameters = detail.get('requestParameters')
    resource_type = derive_resource_type(event)
    if resource_type == 'kinesis':
        return request_parameters.get('streamName')
    elif resource_type == 'dynamodb':
        return request_parameters.get('tableName')
    elif resource_type == 'rds':
        return request_parameters.get('dBInstanceIdentifier')
    elif resource_type == 'elasticloadbalancing':
        return request_parameters.get('name')
    elif resource_type == 'apigateway':
        return request_parameters.get('createRestApiInput').get('name') + '-' + detail.get('responseElements').get('id')
    elif resource_type == 'lambda':
        return request_parameters.get('functionName')        
    elif resource_type == 'redshift':
        return request_parameters.get('clusterIdentifier')
    elif resource_type == 's3':
        return request_parameters.get('bucketName')
    elif resource_type == 'es':
        return request_parameters.get('domainName')
    elif resource_type == 'elasticache':
        return request_parameters.get('cacheClusterId')
    elif resource_type == 'kms':
        return detail.get('responseElements').get('keyMetadata').get('arn')
    else:
        raise Exception('Invalid or not-tracked CloudTrail event of even source {}'.format(event_source))

def derive_resource_arn(event):
    event_source = event.get('source')
    detail = event.get('detail')
    responseElements = detail.get('responseElements')
    resource_type = derive_resource_type(event)
    if resource_type == 'kinesis':
        return None
    elif resource_type == 'dynamodb':
        return responseElements.get('tableDescription').get('tableArn')
    elif resource_type == 'rds':
        return responseElements.get('dBInstanceArn')
    elif resource_type == 'elasticloadbalancing':
        return None
    elif resource_type == 'apigateway':
        return None
    elif resource_type == 'lambda':
        # arn is not guaranteedly being returned
        return None
        # return responseElements.get('functionArn')        
    elif resource_type == 'redshift':
        return None
    elif resource_type == 's3':
        return None
    elif resource_type == 'es':
        return responseElements.get('domainStatus').get('aRN')
    elif resource_type == 'elasticache':
        return None
    else:
        raise Exception('Invalid or not-tracked CloudTrail event of even source {}'.format(event_source))

def derive_resource_type(event):
    return event.get('source').rsplit('.', 1)[1]