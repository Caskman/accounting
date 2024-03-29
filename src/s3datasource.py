import os
import aws
import context
from pathlib import Path


# Downloads data into target dir
# Make sure target dir exists
def download_statement_data(c, target_dir):
    s3 = aws.gets3resource(c)
    BUCKET_ID = c.get_var("BUCKET_ID")
    mybucket = s3.Bucket(BUCKET_ID)

    STATEMENT_PATH = c.get_var("STATEMENT_PATH")
    for obj in mybucket.objects.filter(Prefix=f"{STATEMENT_PATH}/"):
        splits = obj.key.split("/")
        objectname = splits[-1]
        if objectname != "":
            destfilepath = os.path.join(target_dir, objectname)
            mybucket.download_file(obj.key, destfilepath)


def download_bucket_data(c, target_dir):
    s3 = aws.gets3resource(c)
    BUCKET_ID = c.get_var("BUCKET_ID")
    mybucket = s3.Bucket(BUCKET_ID)

    for obj in mybucket.objects.filter():
        if obj.key[-1] == "/":
            continue
        dest_file_path = os.path.join(target_dir, obj.key)
        output_file = Path(dest_file_path)
        output_file.parent.mkdir(exist_ok=True, parents=True)
        mybucket.download_file(obj.key, dest_file_path)


def get_data_source(c):
    s3 = aws.gets3resource(c)
    bucket_id = c.get_var("BUCKET_ID")
    statement_path = c.get_var('STATEMENT_PATH')
    for obj in s3.Bucket(bucket_id).objects.filter(Prefix=f"{statement_path}/"):
        if obj.key.split("/")[-1] != '':
            obj_contents = get_object(s3, bucket_id, obj.key)
            yield (obj.key, obj_contents)


def get_object_with_context(c, key):
    s3 = aws.gets3resource(c)
    BUCKET_ID = c.get_var("BUCKET_ID")
    return get_object(s3, BUCKET_ID, key)


def get_object(s3, bucket_id, key):
    obj = s3.Object(bucket_id, key)
    contents = obj.get()['Body'].read().decode('utf-8')
    return contents


def put_object_with_context(c, key, string_data):
    s3 = aws.gets3resource(c)
    BUCKET_ID = c.get_var("BUCKET_ID")
    obj = s3.Object(BUCKET_ID, key)
    obj.put(Body=string_data)


def get_context():
    c = context.init_context()
    CONFIG_PATH = c.get_var("CONFIG_PATH")
    config = get_object_with_context(c, CONFIG_PATH)
    c.append_raw_vars(config)
    return c


def get_rules_contents(c):
    rules_key = c.get_var('RULES_PATH')
    return get_object_with_context(c, rules_key)


def store_rules_contents(c, rules_data):
    rules_key = c.get_var('RULES_PATH')
    put_object_with_context(c, rules_key, rules_data)


def get_transaction_data(c):
    transaction_data_key = c.get_var('TRANSACTION_DATA_PATH')
    return get_object_with_context(c, transaction_data_key)


def store_transaction_data(c, string_data):
    transaction_data_key = c.get_var('TRANSACTION_DATA_PATH')
    put_object_with_context(c, transaction_data_key, string_data)


def get_auth_token(c):
    auth_token_key = c.get_var('AUTH_TOKEN')
    return auth_token_key


def save_object_from_file_path(context, file_path, object_key):
    s3 = aws.gets3resource(context)
    bucket_id = context.get_var("BUCKET_ID")
    with open(file_path, 'rb') as file_handle:
        s3.Object(bucket_id, object_key).put(Body=file_handle)
