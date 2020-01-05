import json

import s3datasource
import classify
import datainput
import persistence

def csvify_trans(trans):
    stringfields = map(lambda t: str(t), t.field_order())
    csvlines = map(lambda t: "\t".join(stringfields), trans)
    return "\n".join(csvlines)

def jsonify_trans(trans):
    return json.dumps(map(lambda t: t.get_json_dict(), trans))

####################################################################################

def addcors(response):
    if not 'headers' in response:
        response['headers'] = {}
    response['headers']['Access-Control-Allow-Origin'] = '*'
    response['headers']['Access-Control-Allow-Headers'] = '*'
    response['headers']['Access-Control-Allow-Methods'] = '*'
    return response

def response(body):
    return addcors({
        'statusCode': 200,
        'body': json.dumps(body),
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*",
        },
    })

def authenticate(event, c):
    if 'body' not in event:
        return False
    body = json.loads(event['body'])
    given_token = body['auth']
    expected_token = s3datasource.get_auth_token(c)
    return given_token == expected_token

def bad_request():
    return addcors({
        'statusCode': 400,
    })

def bad_auth():
    return addcors({
        'statusCode': 401,
    })

def get_transactions(event, c):
    data = persistence.get_all(c)
    contentType = event['queryStringParameters']['type']
    if contentType == 'csv':
        return response({
            "data": csvify_trans(data),
        })
    elif contentType == 'json':
        return response({
            "data": jsonify_trans(data),
        })
    else:
        return bad_request()

def classify_transactions(event, c):
    # datasource = s3datasource.get_data_source(c)
    # data = datainput.parse_data_source(datasource)
    data = persistence.get_all(c)
    rules_contents = s3datasource.get_rules_contents(c)
    rules = classify.process_rules(rules_contents)
    classify.classify(data, rules)
    persistence.update(c, data)
    # csv_data = "\n".join(map(lambda t: "\t".join(map(lambda f: str(f), t.field_order())), data))
    # s3datasource.store_transaction_data(c, csv_data)
    return response({
        "success": True,
    })

def rules_get(event, c):
    rules_contents = s3datasource.get_rules_contents(c)
    return response({
        "data": rules_contents,
    })

def rules_put(event, c):
    rules_contents = json.loads(event["body"])['rules']
    try:
        classify.process_rules(rules_contents)
    except:
        return bad_request()
    s3datasource.store_rules_contents(c, rules_contents)
    return response({
        "success": True,
    })

routes = {
    'transactions_get': get_transactions,
    'classify': classify_transactions,
    'rules_get': rules_get,
    'rules_put': rules_put,
}

def base(event, lambda_context):
    """
        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format
        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html
        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    my_context = s3datasource.get_context()
    if not authenticate(event, my_context):
        return bad_auth()

    route = event["queryStringParameters"]['route']
    if route in routes:
        return routes[route](event, my_context)
    else:
        return bad_request()

# def options_handler(event, lambda_context):
#     return addcors({
#         'statusCode': 204,
#     })

def testing(event, lambda_context):
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': "just testing",
        })
    }

# def authorize(event, lambda_context):
#     if event

if __name__ == '__main__':
    classify_transactions(None)
