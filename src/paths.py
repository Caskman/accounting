import os


def get_statement_data_path(context):
    LOCAL_DATA_DIR = context.get_var("LOCAL_DATA_DIR")
    STATEMENT_PATH = context.get_var("STATEMENT_PATH")
    return os.path.join(LOCAL_DATA_DIR, STATEMENT_PATH)
