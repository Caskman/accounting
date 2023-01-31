import os
import s3datasource
import paths


def retrieve_data():
    c = s3datasource.get_context()
    local_data_path = paths.get_local_data_path(c)
    if not os.path.isdir(local_data_path):
        os.makedirs(local_data_path)
    s3datasource.download_bucket_data(c, local_data_path)
