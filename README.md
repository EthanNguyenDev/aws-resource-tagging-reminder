# aws-resource-tagging-reminder
## Small app to keep tracks of untagged resources in dev acccounts
Automate email alerts to resource creators those who haven't done required tagging. This is to help platform team to charge infra cost back to application team BU. Thisi s a common issue where the org wants to control security aspect of a few shared AWS accounts with deployment pipelines in places
Powered by AWS Lambda, SES, SNS, CloudTrail, CloudWatch, DynamoDB, Cloudformation.

## By nature, for some AWS resources, tagging can only be done after resource provision. This is why we can't make decisions at the time of CloudTrail event triggered. Also, it's a better idea to keep track all of resources on a regular basic because tags can be updated anytime.

1. In master account
   1. API Gateway + Lambda + SES setup with email template, expose 1 endpoint as centrailized setup for email alert
2. In each dev/shared accounts
   1. Tracking Lambda: CloudTrail event to trigger Lambda upon resources provision (with custom event pattern), persist resource key, type with meta data in DynamoDB
   2. DynamoDB to store key details to lookup resource ARN & tagging later
   3. Reminder Lambda: loop thru all events & check for their existence & valid PC-code tag
      1. If resources no longer exist --> delete in DynamoDB
      2. If resources exist with no (proper) tagging --> group those resources by creator ARN (IAM & federated users) & send email reminder to them by invoking the API setup in master account 

   
   