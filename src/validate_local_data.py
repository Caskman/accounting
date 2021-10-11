import s3datasource
import datainput


def validate_local_data():
    c = s3datasource.get_context()
    LOCAL_DATA_DIR = c.get_var("LOCAL_DATA_DIR")
    datasource = datainput.get_local_data_source(LOCAL_DATA_DIR)
    results = datainput.validate_all_data(datasource)
    num_errors = len(results[0])
    if num_errors > 0:
        print(results[1])
        print()
        print('Errors')
        for e in results[0]:
            print(e)
        print()
        print(f'Total # of Errors: {num_errors}')
