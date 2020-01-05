import boto3

def getsession(c):
    AWS_ACCESS_KEY_ID = c.get_var("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = c.get_var("AWS_SECRET_ACCESS_KEY")
    return boto3.session.Session(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

def gets3resource(c):
    if c.get_var('IN_AWS_LAMBDA') == 'true':
        return boto3.resource('s3')
    session = getsession(c)
    s3 = session.resource("s3")
    return s3

def getdb(c):
    if c.get_var('IN_AWS_LAMBDA') == 'true':
        return boto3.resource('dynamodb')
    return getsession(c).resource('dynamodb')
