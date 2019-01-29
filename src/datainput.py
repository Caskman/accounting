from datetime import datetime
from os import listdir
from os.path import join, abspath
import csv
import re

# DATA FORMATS

BOA_CREDIT = "boacredit"
BOA_DEBIT = "boadebit"
LLBEAN_MCCREDIT = "llbeanmccredit"

"""
Format of filename is <label>_<type>_<date>.csv
"""

def parse_file(filepath):
    filename = filepath.split("/")[-1].replace(".csv", "")
    filenamesplits = filename.split("_")
    if len(filenamesplits) > 3:
        raise Exception(f"{filepath} has an invalid filename")
    
    label, formattype, date = filenamesplits
    filelines = []
    with open(filepath, "r") as fin:
        filelines = fin.readlines()
        filelines = [l[:-1] if l[-1] == "\n" else l for l in filelines]
        
    resultdata = None
    if formattype == BOA_CREDIT:
        resultdata = parse_boacredit(filelines, label)
    elif formattype == BOA_DEBIT:
        resultdata = parse_boadebit(filelines, label)
    elif formattype == LLBEAN_MCCREDIT:
        resultdata = parse_llbeancredit(filelines, label)
    else:
        raise Exception(f"Data type {formattype} is unknown")

    return resultdata

# PARSE FUNCTIONS

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


def get_data(data_dir):
    files = [abspath(join(data_dir, f)) for f in listdir(data_dir) if f[-4:] == ".csv"]

    data = []
    for f in files:
        d = parse_file(f)
        data.extend(d)

    return data

class Transaction():
    def __init__(self, date, desc, amt, label, ref_num):
        self.date = date
        self.desc = desc
        self.amt = amt
        self.label = label
        self.ref_num = ref_num
    def __repl__(self):
        return f"{{ {self.date}, {self.desc}, {self.amt}, {self.label}, {self.ref_num},  }}"
    def __str__(self):
        return self.__repl__()

