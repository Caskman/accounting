import aws
from datainput import Transaction
from boto3.dynamodb.conditions import Key, Attr

def get_trans_table(c):
    return aws.getdb(c).Table('transactions')

def get(c, start_date, end_date, page_start, page_len):
    filterExpression = Attr('date').between(start_date, end_date)
    results = raw_get(c, filterExpression)['Items']
    paginated = results[page_start: page_start + page_len]
    return parse_transactions(paginated)

def get_all(c):
    return parse_transactions(raw_get(c, None)['Items'])

def raw_get(c, filterExpression):
    results = None
    if filterExpression:
        results = get_trans_table(c).scan(FilterExpression=filterExpression)
    else:
        results = get_trans_table(c).scan()
    if 'LastEvaluatedKey' in results:
        raise f'Have hit LastEvaluatedKey, must add pagination now'
    return results

def parse_transactions(items):
    return [Transaction.from_dict(i) for i in items]

def update(c, items):
    with get_trans_table(c).batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item.get_persistent_dict())
