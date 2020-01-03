import json

import s3datasource
import classify
import datainput

def get_transactions(event):
    my_context = s3datasource.get_context()
    data = s3datasource.get_transaction_data(my_context)
    return {
        'statusCode': 200,
        'body': json.dumps({
            "data": data,
        }),
    }

def classify_transactions(event):
    my_context = s3datasource.get_context()
    datasource = s3datasource.get_data_source(my_context)
    data = datainput.parse_data_source(datasource)
    rules_contents = s3datasource.get_rules_contents(my_context)
    rules = classify.process_rules(rules_contents)
    classify.classify(data, rules)
    csv_data = "\n".join(map(lambda t: "\t".join(map(lambda f: str(f), t.field_order())), data))
    # csv_rows = map(lambda t: "\t".join(t.field_order), data)
    # csv_data = "\n".join(csv_rows)

    # json_data = json.dumps([d.get_dict() for d in data])
    s3datasource.store_transaction_data(my_context, csv_data)
    return {
        'statusCode': 200,
        'body': json.dumps({
            "success": True,
        }),
    }

def rules_get(event):
    my_context = s3datasource.get_context()
    rules_contents = s3datasource.get_rules_contents(my_context)
    return {
        'statusCode': 200,
        'body': json.dumps({
            "data": rules_contents,
        }),
    }

def rules_put(event):
    rules_contents = event["body"]["rules"]
    my_context = s3datasource.get_context()
    s3datasource.store_rules_contents(my_context, rules_contents)
    return {
        'statusCode': 200,
        'body': json.dumps({
            "success": True,
        }),
    }

routes = {
    'get_transactions': get_transactions,
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
