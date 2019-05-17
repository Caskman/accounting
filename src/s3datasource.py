import boto3
import os

def gets3resource(c):
    AWS_ACCESS_KEY_ID = c.get_var("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = c.get_var("AWS_SECRET_ACCESS_KEY")
    session = boto3.session.Session(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    s3 = session.resource("s3")
    return s3

def download_data(c, target_dir):
    s3 = gets3resource(c)
    BUCKET_ID = c.get_var("BUCKET_ID")
    mybucket = s3.Bucket(BUCKET_ID)

    STATEMENT_PATH = c.get_var("STATEMENT_PATH")
    for obj in mybucket.objects.filter(Prefix=f"{STATEMENT_PATH}/"):
        splits = obj.key.split("/")
        objectname = splits[-1]
        if objectname != "":
            destfilepath = os.path.join(target_dir, objectname)
            mybucket.download_file(obj.key, destfilepath)

def get_object(c, key):
    s3 = gets3resource(c)
    BUCKET_ID = c.get_var("BUCKET_ID")
    obj = s3.Object(BUCKET_ID, key)
    contents = obj.get()['Body'].read().decode('utf-8')
    return contents
