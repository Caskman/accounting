import datetime
import os

import s3datasource
import spreadsheet
import datainput

def compile_statements():
    c = s3datasource.get_context()
    LOCAL_DATA_DIR = c.get_var("LOCAL_DATA_DIR")

    datasource = datainput.get_local_data_source(LOCAL_DATA_DIR)
    data = datainput.parse_data_source(datasource)

    run_id = c.get_run_id()
    outputpath = os.path.join(LOCAL_DATA_DIR, f"aaa-output-{run_id}.xlsx")

    resultfilepath = spreadsheet.build_spreadsheet(c, data, outputpath)
    return outputpath

if __name__ == "__main__":
    compile_statements()
