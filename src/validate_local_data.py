import s3datasource
import datainput

if __name__ == "__main__":
    c = s3datasource.get_context()
    LOCAL_DATA_DIR = c.get_var("LOCAL_DATA_DIR")
    datasource = datainput.get_local_data_source(LOCAL_DATA_DIR)
    datainput.output_data_validation(datasource)


