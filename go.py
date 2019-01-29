import datetime
import os

import s3datasource
import context
import spreadsheet
import datainput

TEMP_DIR = "temp"

def main():
    run_id = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
    temp_dir = f"{TEMP_DIR}-{run_id}"

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    c = context.init_context()
    CONFIG_PATH = c.get_var("CONFIG_PATH")
    config = s3datasource.get_object(c, CONFIG_PATH)
    c.append_raw_vars(config)

    s3datasource.download_data(c, temp_dir)
    data = datainput.get_data(temp_dir)
    outputpath = os.path.join(temp_dir, f"aaa-output-{run_id}.xlsx")

    resultfilepath = spreadsheet.build_spreadsheet(c, data, outputpath)

if __name__ == "__main__":
    main()
