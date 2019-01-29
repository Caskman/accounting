import datetime
import os

from s3datasource import download_data
from envvars import get_var
from spreadsheet import build_spreadsheet
from datainput import get_data

TEMP_DIR = get_var("TEMP_DIR")

def main():
    run_id = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
    temp_dir = f"{TEMP_DIR}-{run_id}"

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    download_data(temp_dir)
    data = get_data(temp_dir)
    outputpath = os.path.join(temp_dir, f"aaa-output-{run_id}.xlsx")

    resultfilepath = build_spreadsheet(data, outputpath)

if __name__ == "__main__":
    main()
