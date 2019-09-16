import boto3

# Create SES client
AWS_REGION = "us-east-1"
ses = boto3.client('ses', AWS_REGION)

BODY = "We believe that you have created below resources without specifying PC-Code tag. Kindly go to AWS Console & update it. \r\n"
BODY_HTML = "<html><head> <style> table { font-family: arial, sans-serif; border-collapse: collapse; width: 100%; } td, th { border: 1px solid #dddddd; text-align: left; padding: 8px; } thead tr:first-child { background-color: #ff9d00; } </style></head><body> <h3>We believe that you have created below resources without specifying PC-Code tag. Kindly go to AWS Console & update it.</h3> <table> <thead> <tr> <th>AWS Account Id</th> <th>Resource Name</th> <th>Resource Type</th> <th>Created Date</th> <th>Creator</th> <th>Remarks</th> </tr> </thead> <tbody> {{#each resources}} <tr> <td>{{ ../account_id }}</td> <td>{{ ResourceKey }}</td> <td>{{ ResourceType }}</td> <td>{{ CreatedDate }}</td> <td>{{ ../recipient_email }}</td>  <td>{{ ResourceMetadata}}</td> </tr> {{/each}} </tbody> </table></body></html>"
# BODY_HTML = """
#     <html>
#     <head></head>
#     <body>
#     </body>
#     </html>
#                 """ 

#response = ses.create_template(
response = ses.update_template(
  Template = {
    'TemplateName' : 'ResourceTaggingAlert',
    'SubjectPart'  : 'Gentle Reminder - Please specify PC-Code tag to your provisioned AWS resources',
    'TextPart'     : BODY,
    'HtmlPart'     : BODY_HTML
  }
)
