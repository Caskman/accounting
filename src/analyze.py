from enum import Enum
import os

import s3datasource
import spreadsheet
import datainput
from classify import yaml
import compile
import console


def standard_compilation(cutoffmonths: int):
    c = s3datasource.get_context()
    LOCAL_DATA_DIR = c.get_var("LOCAL_DATA_DIR")

    # Load classification rules
    rules_contents = None
    with open('classification_rules.yaml', 'r') as fin:
        rules_contents = fin.read()
    rules = yaml.process_rules(rules_contents)

    # Load data
    datasource = datainput.get_local_data_source(LOCAL_DATA_DIR)
    data_all_time = datainput.parse_data_source(datasource)

    # compile data into a single object
    finances = compile.compile_data(
        data_all_time, rules, compile.get_date_months_ago(cutoffmonths))

    return finances


def analyze(summaryonly: bool, monthlyonly: bool, cutoffmonths: int, spreadsheetout: bool):
    c = s3datasource.get_context()
    LOCAL_DATA_DIR = c.get_var("LOCAL_DATA_DIR")

    finances = standard_compilation(cutoffmonths)

    # print data to console
    if monthlyonly or not summaryonly:
        console.console_print_monthly(finances)

    if summaryonly or not monthlyonly:
        console.console_print_summary(finances)

    # output data to excel file
    if spreadsheetout:
        run_id = c.get_run_id()
        outputpath = os.path.join(LOCAL_DATA_DIR, f"aaa-output-{run_id}.xlsx")
        spreadsheet.create_spreadsheet(finances, outputpath)

    console.print_classification_errors(finances)


class AnalysisDataValidation(Enum):
    SUCCESS = 0
    MISSING_DATA = 1
    DATA_ERRORS = 2


def analyze_validation() -> AnalysisDataValidation:
    c = s3datasource.get_context()
    LOCAL_DATA_DIR = c.get_var("LOCAL_DATA_DIR")

    if not datainput.validate_data_availability(LOCAL_DATA_DIR):
        return AnalysisDataValidation.MISSING_DATA

    datasource = datainput.get_local_data_source(LOCAL_DATA_DIR)
    data_validation = datainput.validate_all_data(datasource)

    if len(data_validation[0]) > 0:
        return AnalysisDataValidation.DATA_ERRORS

    return AnalysisDataValidation.SUCCESS
