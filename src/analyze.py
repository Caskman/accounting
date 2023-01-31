from enum import Enum
import os

import s3datasource
import spreadsheet
import datainput
from classify import yaml
import compile
import console
import paths


def standard_compilation(cutoffmonths: int):
    context = s3datasource.get_context()
    data_all_time = datainput.get_parsed_local_data(context)

    # Load classification rules
    rules_contents = yaml.get_rules_string(context)
    rules = yaml.process_rules(rules_contents)

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
    statement_data_path = paths.get_statement_data_path(c)

    if not datainput.validate_data_availability(statement_data_path):
        return AnalysisDataValidation.MISSING_DATA

    datasource = datainput.get_local_data_source(statement_data_path)
    data_validation = datainput.validate_all_data(datasource)

    if len(data_validation[0]) > 0:
        return AnalysisDataValidation.DATA_ERRORS

    return AnalysisDataValidation.SUCCESS
