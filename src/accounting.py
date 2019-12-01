import datetime
import os

import s3datasource
import spreadsheet
import datainput

def compile_statements():
    temp_dir = datainput.get_temp_dir_relative_path()

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    c = s3datasource.get_context()

    s3datasource.download_data(c, temp_dir)
    data = datainput.get_data(temp_dir)
    outputpath = os.path.join(temp_dir, f"aaa-output-{run_id}.xlsx")

    resultfilepath = spreadsheet.build_spreadsheet(c, data, outputpath)
    return outputpath

if __name__ == "__main__":
    compile_statements()
