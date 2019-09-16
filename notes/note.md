# DynamoDB Table (CloudTrailEventResourceTracking)
event_id (hashkey, event.id) string
creator_arn (sortkey) string
resource_key   string (used for email) 
resource_type  string (used for email)
resource_meta_data json (used for email)
resource_created_date (derived from event.time)
email_sent_once: true/false 
should_send_email: string 'x' or no value (send email if 'x')
created_date: string ISO datetime
original_event cloudwatch event (optional) (json)

#GSI (sparse index)
ShouldSendEmail (hashKey)
CreatorArn
ResourceType
ResourceKey
ResourceCreated_date
ResourceMetadata (json)


#Kinesis (CreateStream)
Creator: CloudTrailevent --> detail --> userIdentity --> arn
ResourceKey: CloudTrailevent -->  requestParameters --> streamName
resource_meta_data: 
    CloudTrailevent -->  detail --> awsRegion (ap-southeast-1)
    CloudTrailevent -->  requestParameters --> shardCount (1)

#RDS (CreateDBInstance)
Creator: CloudTrailevent --> detail --> userIdentity --> arn
ResourceKey: CloudTrailevent -->  requestParameters --> dBInstanceIdentifier
resource_meta_data: 
    CloudTrailevent -->  detail --> awsRegion (ap-southeast-1)
    CloudTrailevent -->  requestParameters --> dBInstanceClass (db.t2.micro)

#API Gateway (CreateRestApi)
Creator: CloudTrailevent --> detail --> userIdentity --> arn
ResourceKey: CloudTrailevent -->  requestParameters --> createRestApiInput --> name
resource_meta_data: None

#EC2 (RunInstances)
Creator: CloudTrailevent --> detail --> userIdentity --> arn
ResourceKey: CloudTrailevent -->  requestParameters --> dBInstanceIdentifier
resource_meta_data: 
    CloudTrailevent -->  detail --> awsRegion (ap-southeast-1)
    CloudTrailevent -->  requestParameters --> instanceType (t2.micro)

#Elastic LoadBalancer (CreateLoadBalancer)
Creator: CloudTrailevent --> detail --> userIdentity --> arn
ResourceKey: CloudTrailevent -->  requestParameters --> loadBalancerName
resource_meta_data: 
    CloudTrailevent -->  detail --> awsRegion (ap-southeast-1)
    CloudTrailevent -->  requestParameters --> scheme (internet-facing|internal)

#Lambda (CreateFunction20150331)
Creator: CloudTrailevent --> detail --> userIdentity --> arn
ResourceKey: CloudTrailevent -->  requestParameters --> functionName
resource_meta_data: 
    CloudTrailevent -->  detail --> awsRegion (ap-southeast-1)
    CloudTrailevent -->  requestParameters --> memorySize (128: number)
    CloudTrailevent -->  requestParameters --> runtime (nodejs10.x: string)

#S3 (CreateBucket)
Creator: CloudTrailevent --> detail --> userIdentity --> arn
ResourceKey: CloudTrailevent -->  requestParameters --> bucketName
resource_meta_data: 
    CloudTrailevent -->  detail --> awsRegion (ap-southeast-1)

#DynamoDB (CreateTable)
Creator: CloudTrailevent --> detail --> userIdentity --> arn
ResourceKey: CloudTrailevent -->  requestParameters --> tableDescription --> tableName 
resource_meta_data: 
    CloudTrailevent -->  detail --> awsRegion (ap-southeast-1)
    CloudTrailevent -->  requestParameters --> tableDescription --> tableArn (arn:aws:dynamodb:ap-southeast-1:773642266546:table/test) 
    CloudTrailevent -->  requestParameters --> tableDescription --> "provisionedThroughput": {
                                                                        "readCapacityUnits": 5.0,
                                                                        "writeCapacityUnits": 5.0,
                                                                        "numberOfDecreasesToday": 0.0
                                                                    },
#Redshift (CreateCluster)
Creator: CloudTrailevent --> detail --> userIdentity --> arn
ResourceKey: CloudTrailevent -->  requestParameters --> clusterIdentifier
resource_meta_data: 
    CloudTrailevent -->  detail --> awsRegion (ap-southeast-1)
    CloudTrailevent -->  requestParameters --> numberOfNodes, nodeType, clusterType

#ElasticCache (CreateCacheCluster)
Creator: CloudTrailevent --> detail --> userIdentity --> arn
ResourceKey: CloudTrailevent -->  requestParameters --> cacheClusterId
resource_meta_data: 
    CloudTrailevent -->  detail --> awsRegion (ap-southeast-1)
    CloudTrailevent -->  requestParameters --> cacheNodeType (cache.t2.micro)
    CloudTrailevent -->  requestParameters --> engine  (memcached)


#ElasticSearch - CreateElasticsearchDomain
Creator: CloudTrailevent --> detail --> userIdentity --> arn
ResourceKey: CloudTrailevent -->  requestParameters --> domainName
resource_meta_data: 
    CloudTrailevent -->  detail --> awsRegion (ap-southeast-1)
    CloudTrailevent -->  requestParameters --> cacheNodeType (cache.t2.micro)
    CloudTrailevent -->  requestParameters --> elasticsearchVersion, elasticsearchClusterConfig {}