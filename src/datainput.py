from datetime import datetime
from os import listdir
from os.path import join, abspath
import csv
import re

# DATA FORMATS

BOA_CREDIT = "boacredit"
BOA_DEBIT = "boadebit"
LLBEAN_MCCREDIT = "llbeanmccredit"
CHASE_CREDIT = "chasecredit"

"""
Format of filename is <label>_<type>_<date>.csv
"""

def parse_file(filepath, filecontents):
    filename = filepath.split("/")[-1].replace(".csv", "")
    filenamesplits = filename.split("_")
    if len(filenamesplits) > 3:
        raise Exception(f"{filepath} has an invalid filename")
    
    label, formattype, date = filenamesplits
    filelines = [l for l in filecontents.split('\n') if l.strip() != '']
        
    resultdata = None
    if formattype == BOA_CREDIT:
        resultdata = parse_boacredit(filelines, label)
    elif formattype == BOA_DEBIT:
        resultdata = parse_boadebit(filelines, label)
    elif formattype == LLBEAN_MCCREDIT:
        resultdata = parse_llbeancredit(filelines, label)
    elif formattype == CHASE_CREDIT:
        resultdata = parse_chasecredit(filelines, label)
    else:
        raise Exception(f"Data type {formattype} is unknown")

    return resultdata

# PARSE FUNCTIONS

def parse_chasecredit(lines, label):
    parsed_lines = list(csv.reader(lines))
    parsed_lines = parsed_lines[1:]
    return_data = []
    for row in parsed_lines:
        if len(row) != 6:
            raise Exception(f"Invalid number of cols for label: {label} data type: {CHASE_CREDIT} cols: {len(row)}")
        
        date = datetime.strptime(row[1], "%m/%d/%Y").date()
        amount = float(re.sub(r"\"|\$", "", row[5]))
        description = f"{row[2]}; {row[3]}; {row[4]}"

        new_item = Transaction(
            date,
            description,
            amount,
            label,
            None,
        )
        return_data.append(new_item)

    return return_data

def parse_llbeancredit(lines, label):
    parsed_lines = list(csv.reader(lines, dialect='excel-tab'))
    return_data = []
    for row in parsed_lines:
        if len(row) < 4:
            raise Exception(f"Invalid number of cols for label: {label} data type: {LLBEAN_MCCREDIT} cols: {len(row)}")
        
        date = datetime.strptime(row[0], "%m/%d/%Y").date()
        amount = float(re.sub(r"\"|\$", "", row[1]))
        description = row[2]

        new_item = Transaction(
            date,
            description,
            amount,
            label,
            None,
        )
        return_data.append(new_item)

    return return_data

def parse_boacredit(lines, label):
    parsed_lines = list(csv.reader(lines))
    parsed_lines = parsed_lines[1:]
    return_data = []
    for row in parsed_lines:
        if len(row) < 5:
            raise Exception(f"Invalid number of cols for label: {label} data type: {BOA_CREDIT} cols: {len(row)}")

        date = datetime.strptime(row[0], "%m/%d/%Y").date()
        reference_number = row[1]
        description = row[2]
        amount = float(re.sub(r"\"", "", row[4]))

        new_item = Transaction(
            date,
            description,
            amount,
            label,
            reference_number,
        )
        return_data.append(new_item)

    return return_data

def parse_boadebit(lines, label):
    parsed_lines = list(csv.reader(lines))
    parsed_lines = parsed_lines[8:]
    return_data = []
    for row in parsed_lines:
        if len(row) < 3:
            raise Exception(f"Invalid number of cols for label: {label} data type: {BOA_DEBIT} cols: {len(row)}")
        
        date = datetime.strptime(row[0], "%m/%d/%Y").date()
        description = row[1]
        amount = float(re.sub(r"\"", "", row[2]))

        new_item = Transaction(
            date,
            description,
            amount,
            label,
            None,
        )
        return_data.append(new_item)

    return return_data


# END PARSE FUNCTIONS

# DATA SOURCES

def get_local_data_source(data_dir):
    files = [abspath(join(data_dir, f)) for f in listdir(data_dir) if f[-4:] == ".csv"]
    for f in files:
        contents = ''
        with open(f, 'r') as fin:
            contents = fin.read()
        yield (f, contents)


# END DATA SOURCES


def parse_data_source(datasource):
    data = []
    for filepath, contents in datasource:
        d = parse_file(filepath, contents)
        data.extend(d)

    return data

TEMP_DIR = "temp"

def parse_data_source_last_month(datasource):
    data = parse_data_source(datasource)
    today = datetime.now().date()
    data_last_month = filter(lambda t: (today - t.date).days <= 30, data)
    return data_last_month

class Transaction():
    def __init__(self, date, desc, amt, label, ref_num, classification='none'):
        self.date = date
        self.desc = desc
        self.amt = amt
        self.label = label
        self.ref_num = ref_num
        self.classification = classification
        self.classification_debug = ''
    def field_order(self):
        return [
            self.date,
            self.amt,
            self.desc,
            self.label,
            self.ref_num,
            self.classification,
        ]
    def __repl__(self):
        field_list = self.field_order()
        field_string = ", ".join(field_list)
        return f"{{ {field_string} }}"
    def __str__(self):
        return self.__repl__()

    def get_dict(self):
        d = self.__dict__
        d["date"] = d["date"].isoformat()
        return d

