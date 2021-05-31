import os
import s3datasource


if __name__ == "__main__":
    c = s3datasource.get_context()
    LOCAL_DATA_DIR = c.get_var("LOCAL_DATA_DIR")
    if not os.path.isdir(LOCAL_DATA_DIR):
        os.mkdir(LOCAL_DATA_DIR)
    s3datasource.download_data(c,LOCAL_DATA_DIR)

