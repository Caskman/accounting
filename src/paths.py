import os


def get_local_data_path(context):
    return context.get_var("LOCAL_DATA_DIR")


def get_statement_data_path(context):
    LOCAL_DATA_DIR = context.get_var("LOCAL_DATA_DIR")
    STATEMENT_PATH = context.get_var("STATEMENT_PATH")
    return os.path.join(LOCAL_DATA_DIR, STATEMENT_PATH)


def get_classification_rules_file_path(context):
    LOCAL_DATA_DIR = context.get_var("LOCAL_DATA_DIR")
    RULES_PATH = context.get_var("RULES_PATH")
    return os.path.join(LOCAL_DATA_DIR, RULES_PATH)
