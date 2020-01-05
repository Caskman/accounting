import uuid
import s3datasource
import datainput
import persistence

def insert_transactions(c, trans):
    db = s3datasource.getdb(c)
    trans_table = db.Table('transactions')
    with trans_table.batch_writer() as batch:
        for tran in trans:
            batch.put_item(
                Item=tran.get_persistent_dict()
            )

def upload_data(c, data):
    # my_context = s3datasource.get_context()
    # LOCAL_DATA_DIR = my_context.get_var("LOCAL_DATA_DIR")
    # datasource = datainput.get_local_data_source(LOCAL_DATA_DIR)
    # data = datainput.parse_data_source(datasource)
    chosen_data = data
    for d in chosen_data:
        d.id = uuid.uuid4()
    insert_transactions(c, chosen_data)

def main():
    my_context = s3datasource.get_context()
    # results = persistence.get_all(my_context)
    results = persistence.get(my_context, '2019-11-01', '2019-11-31', 0, 25)
    print(len(results))
    import json
    print(json.dumps(results[0].get_json_dict()))
    # db = s3datasource.getdb(my_context)
    # scan_result = db.Table('transactions').scan()
    # print(type(scan_result))
    # print(scan_result.keys())
    # print(scan_result['Count'])
    # print(scan_result['ScannedCount'])
    # print(scan_result['LastEvaluatedKey'])

if __name__ == '__main__':
    main()
