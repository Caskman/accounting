import json

import s3datasource
import classify
import datainput
# import boto3
# import os

# s3 = boto3.resource('s3')

def lambda_handler(event, lambda_context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    my_context = s3datasource.get_context()
    datasource = s3datasource.get_data_source(my_context)
    data = datainput.parse_data_source(datasource)
    rules_contents = s3datasource.get_rules_contents(my_context)
    rules = classify.process_rules(rules_contents)
    classify.classify(data, rules)

    return {
        'statusCode': 200,
        'body': json.dumps({
            "data": [d.get_dict() for d in data],
        }),
    }

if __name__ == '__main__':
    response = lambda_handler('blah', 'blah')
    with open('lambda_response.json','w') as fout:
        fout.write(response['body'])
