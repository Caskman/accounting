import os

import s3datasource
import spreadsheet
import datainput
import classify
import compile
import console


def compile_data_into_spreadsheet():
    c = s3datasource.get_context()
    LOCAL_DATA_DIR = c.get_var("LOCAL_DATA_DIR")

    datasource = datainput.get_local_data_source(LOCAL_DATA_DIR)
    data = datainput.parse_data_source(datasource)

    run_id = c.get_run_id()
    outputpath = os.path.join(LOCAL_DATA_DIR, f"aaa-output-{run_id}.xlsx")

    spreadsheet.build_spreadsheet(c, data, outputpath)
    return outputpath


def run():
    c = s3datasource.get_context()
    LOCAL_DATA_DIR = c.get_var("LOCAL_DATA_DIR")

    # Load classification rules
    rules_contents = None
    with open('classification_rules.csv', 'r') as fin:
        rules_contents = fin.read()
    rules = classify.process_rules(rules_contents)

    # Load data
    datasource = datainput.get_local_data_source(LOCAL_DATA_DIR)
    data_all_time = datainput.parse_data_source(datasource)

    # compile data into a single object
    finances = compile.compile_data(data_all_time, rules)

    # print data to console
    console.console_print(finances)


if __name__ == "__main__":
    run()
