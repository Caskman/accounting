import sys
import datainput
import classify
import s3datasource

def convert_transaction_to_string(transaction):
    prop_list = [
        transaction.desc,
        transaction.classification,
        transaction.amt,
        transaction.date,
        transaction.label,
    ]
    first = True
    line = ""
    for prop in prop_list:
        newline = '' if first else '\t'
        line += f"{newline}{prop}"
        first = False
    return line

def create_transaction_csv_blob(transactions):
    transaction_lines = map(convert_transaction_to_string, transactions)
    transaction_blob = "\n".join(transaction_lines)
    return transaction_blob


if len(sys.argv) != 2:
    raise Exception("must have one argument which is the rules file")


c = s3datasource.get_context()
LOCAL_DATA_DIR = c.get_var("LOCAL_DATA_DIR")

data = list(datainput.get_data_last_month(LOCAL_DATA_DIR))
rules_contents = None
with open(sys.argv[1],'r') as fin:
    rules_contents = fin.read()
rules = classify.process_rules(rules_contents)
classify.classify(data, rules)
transaction_blob = create_transaction_csv_blob(data)
with open('classified_transactions.csv','w') as fout:
    fout.write(transaction_blob)

