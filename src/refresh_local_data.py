import os

import s3datasource

def refresh_local_data():
    c = s3datasource.get_context()

    LOCAL_DATA_DIR = c.get_var("LOCAL_DATA_DIR")

    if not os.path.exists(LOCAL_DATA_DIR):
        os.makedirs(LOCAL_DATA_DIR)

    s3datasource.download_data(c, LOCAL_DATA_DIR)

if __name__ == "__main__":
    refresh_local_data()
