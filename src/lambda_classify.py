import json

import s3datasource
import classify
import datainput

def response(body):
    return {
        'statusCode': 200,
        'body': json.dumps(body),
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*",
        },
    }


def get_transactions(event):
    my_context = s3datasource.get_context()
    data = s3datasource.get_transaction_data(my_context)
    return response({
        "data": data,
    })

def classify_transactions(event):
    my_context = s3datasource.get_context()
    datasource = s3datasource.get_data_source(my_context)
    data = datainput.parse_data_source(datasource)
    rules_contents = s3datasource.get_rules_contents(my_context)
    rules = classify.process_rules(rules_contents)
    classify.classify(data, rules)
    csv_data = "\n".join(map(lambda t: "\t".join(map(lambda f: str(f), t.field_order())), data))
    s3datasource.store_transaction_data(my_context, csv_data)
    return response({
        "success": True,
    })

def rules_get(event):
    my_context = s3datasource.get_context()
    rules_contents = s3datasource.get_rules_contents(my_context)
    return response({
        "data": rules_contents,
    })

def rules_put(event):
    rules_contents = json.loads(event["body"])['rules']
    my_context = s3datasource.get_context()
    try:
        classify.process_rules(rules_contents)
    except:
        return {
            'statusCode': 400
        }
    s3datasource.store_rules_contents(my_context, rules_contents)
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

    params = event["queryStringParameters"]
    route = params['route']
    if route in routes:
        return routes[route](event)
    else:
        raise Exception(f'Unknown route {route}')

if __name__ == '__main__':
    classify_transactions(None)
