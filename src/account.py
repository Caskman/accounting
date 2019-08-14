import datetime
import os

import s3datasource
import context
import spreadsheet
import datainput

TEMP_DIR = "temp"

def get_temp_dir():
    run_id = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
    temp_dir = f"{TEMP_DIR}-{run_id}"
    return temp_dir


def compile_statements():
    temp_dir = get_temp_dir()

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
    return outputpath

def verify_and_upload(json_dict):
    year = json_dict["year"]
    month = json_dict["month"]
    accountType = json_dict["accountType"]
    contents = json_dict["contents"]
    label = json_dict["label"]

    lines = [line.strip() for line in contents.split("\n")]
    success, transactions, error_msg = datainput.parse_lines(lines, accountType, label)

    if not success:
        abort(400, error_msg)

    normalized_contents = datainput.normalize_to_string(transactions)

    filename = f"{label}_norm_{year}-{month}.csv"

    temp_dir = get_temp_dir()
    filepath = os.path.join(temp_dir, filename)
    with open(filepath, "w") as fin:
        fin.write(normalized_contents)
    
    success = s3datasource.put_statement(filepath, filename)
    return success

if __name__ == "__main__":
    compile()
