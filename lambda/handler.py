import json

def lambda_handler(event, context):
    my_invalid_function()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from CDK 2.0!')
    }
