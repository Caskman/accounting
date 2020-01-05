from decimal import Decimal
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
Format of filename is <source>_<type>_<date>.csv
"""

def parse_file(filepath, filecontents):
    filename = filepath.split("/")[-1].replace(".csv", "")
    filenamesplits = filename.split("_")
    if len(filenamesplits) > 3:
        raise Exception(f"{filepath} has an invalid filename")
    
    source, formattype, date = filenamesplits
    filelines = [l for l in filecontents.split('\n') if l.strip() != '']
        
    resultdata = None
    if formattype == BOA_CREDIT:
        resultdata = parse_boacredit(filelines, source)
    elif formattype == BOA_DEBIT:
        resultdata = parse_boadebit(filelines, source)
    elif formattype == LLBEAN_MCCREDIT:
        resultdata = parse_llbeancredit(filelines, source)
    elif formattype == CHASE_CREDIT:
        resultdata = parse_chasecredit(filelines, source)
    else:
        raise Exception(f"Data type {formattype} is unknown")

    return resultdata

# PARSE FUNCTIONS

def parse_chasecredit(lines, source):
    parsed_lines = list(csv.reader(lines))
    parsed_lines = parsed_lines[1:]
    return_data = []
    for row in parsed_lines:
        if len(row) != 6:
            raise Exception(f"Invalid number of cols for source: {source} data type: {CHASE_CREDIT} cols: {len(row)}")
        
        date = datetime.strptime(row[1], "%m/%d/%Y").date()
        amount = Decimal(re.sub(r"\"|\$", "", row[5]))
        description = f"{row[2]}; {row[3]}; {row[4]}"

        new_item = Transaction(
            None,
            date,
            description,
            amount,
            source,
            None,
        )
        return_data.append(new_item)

    return return_data

def parse_llbeancredit(lines, source):
    parsed_lines = list(csv.reader(lines, dialect='excel-tab'))
    return_data = []
    for row in parsed_lines:
        if len(row) < 4:
            raise Exception(f"Invalid number of cols for source: {source} data type: {LLBEAN_MCCREDIT} cols: {len(row)}")
        
        date = datetime.strptime(row[0], "%m/%d/%Y").date()
        amount = Decimal(re.sub(r"\"|\$", "", row[1]))
        description = row[2]

        new_item = Transaction(
            None,
            date,
            description,
            amount,
            source,
            None,
        )
        return_data.append(new_item)

    return return_data

def parse_boacredit(lines, source):
    parsed_lines = list(csv.reader(lines))
    parsed_lines = parsed_lines[1:]
    return_data = []
    for row in parsed_lines:
        if len(row) < 5:
            raise Exception(f"Invalid number of cols for source: {source} data type: {BOA_CREDIT} cols: {len(row)}")

        date = datetime.strptime(row[0], "%m/%d/%Y").date()
        reference_number = row[1]
        description = row[2]
        amount = Decimal(re.sub(r"\"", "", row[4]))

        new_item = Transaction(
            None,
            date,
            description,
            amount,
            source,
            reference_number,
        )
        return_data.append(new_item)

    return return_data

def parse_boadebit(lines, source):
    parsed_lines = list(csv.reader(lines))
    parsed_lines = parsed_lines[8:]
    return_data = []
    for row in parsed_lines:
        if len(row) < 3:
            raise Exception(f"Invalid number of cols for source: {source} data type: {BOA_DEBIT} cols: {len(row)}")
        
        date = datetime.strptime(row[0], "%m/%d/%Y").date()
        description = row[1]
        amount = Decimal(re.sub(r"\"", "", row[2]))

        new_item = Transaction(
            None,
            date,
            description,
            amount,
            source,
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
    def __init__(self, identifier, date, desc, amt, source, ref_num, classification='none'):
        self.id = identifier
        self.date = date
        self.desc = desc
        self.amt = amt
        self.source = source
        self.ref_num = ref_num
        self.classification = classification
        self.classification_debug = ''
    @staticmethod
    def from_dict(d):
        return Transaction(
            str(d['id']),
            datetime.strptime(d['date'], "%Y-%m-%d").date(),
            str(d['desc']),
            Decimal(d['amt']),
            str(d['source']),
            str(d['ref_num']),
            str(d['classification']),
        )
    def get_persistent_dict(self):
        return {
            'id': str(self.id),
            'date': str(self.date.isoformat()),
            'desc': str(self.desc),
            'amt': Decimal(self.amt),
            'source': str(self.source),
            'ref_num': str(self.ref_num),
            'classification': str(self.classification),
        }
    def get_json_dict(self):
        d = self.get_persistent_dict()
        d['amt'] = float(d['amt'])
        return d
    def field_order(self):
        return [
            self.id,
            self.date,
            self.amt,
            self.desc,
            self.classification,
            self.source,
            self.ref_num,
        ]
    def __repl__(self):
        field_list = map(lambda t: str(t),self.field_order())
        field_string = ", ".join(field_list)
        return f"{{ {field_string} }}"
    def __str__(self):
        return self.__repl__()


