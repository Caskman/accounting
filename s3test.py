import boto3
from envvars import get_var
import os

AWS_ACCESS_KEY_ID = get_var("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = get_var("AWS_SECRET_ACCESS_KEY")
BUCKET_ID = get_var("BUCKET_ID")
STATEMENT_PATH = get_var("STATEMENT_PATH")

def download_data(target_dir):
    session = boto3.session.Session(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

    s3 = session.resource("s3")
    mybucket = s3.Bucket(BUCKET_ID)

    for obj in mybucket.objects.filter(Prefix=f"{STATEMENT_PATH}/"):
        print(obj.key)
        splits = obj.key.split("/")
        objectname = splits[-1]
        if objectname != "":
            destfilepath = os.path.join(target_dir, objectname)
            mybucket.download_file(obj.key, destfilepath)

if __name__ == "__main__":
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    download_data(test_dir)
