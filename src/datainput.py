from decimal import Decimal
from datetime import datetime
import os
from os import error, listdir
from os.path import join, abspath
import csv
import re
from typing import Sequence


class Transaction():
    def __init__(self, identifier, date, desc, amt, source, ref_num=None, classification='none', memo=''):
        self.id = identifier
        self.date = date
        self.desc = desc
        self.amt = amt
        self.source = source
        self.ref_num = ref_num
        self.classification = classification
        self.classification_debug = ''
        self.memo = memo

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
            str(d['memo']),
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
            'memo': str(self.memo),
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
            self.memo,
            self.classification,
            self.source,
            self.ref_num,
        ]

    def __repl__(self):
        field_list = map(lambda t: str(t), self.field_order())
        field_string = ", ".join(field_list)
        return f"{{ {field_string} }}"

    def __str__(self):
        return self.__repl__()

# DATA FORMATS


BOA_CREDIT = "boacredit"
BOA_DEBIT = "boadebit"
LLBEAN_MCCREDIT = "llbeanmccredit"
CHASE_CREDIT = "chasecredit"

"""
Format of filename is <source>_<type>_<date>.csv
"""


def parse_file(filepath, filecontents) -> Sequence[Transaction]:
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


def parse_chasecredit(lines, source) -> Sequence[Transaction]:
    if 'Transaction Date,Post Date,Description,Category,Type,Amount' not in lines[0]:
        raise Exception('Unrecognized file format for source: {source}')

    parsed_lines = list(csv.reader(lines))
    parsed_lines = parsed_lines[1:]
    return_data = []
    for row in parsed_lines:
        if not len(row) in [6, 7]:
            raise Exception(
                f"Invalid number of cols for source: {source} data type: {CHASE_CREDIT} cols: {len(row)}\nRow is:\n{row}")

        date = datetime.strptime(row[1], "%m/%d/%Y").date()
        amount = Decimal(re.sub(r"\"|\$", "", row[5]))
        description = f"{row[2]}; {row[3]}; {row[4]}"
        memo = None
        if len(row) == 7:
            memo = row[6]

        new_item = Transaction(
            None,
            date,
            description,
            amount,
            source,
            memo=memo,
        )
        return_data.append(new_item)

    return return_data


def parse_llbeancredit(lines, source) -> Sequence[Transaction]:
    parsed_lines = list(csv.reader(lines, dialect='excel-tab'))
    return_data = []
    for row in parsed_lines:
        if len(row) < 4:
            raise Exception(
                f"Invalid number of cols for source: {source} data type: {LLBEAN_MCCREDIT} cols: {len(row)}")

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


def parse_boacredit(lines, source) -> Sequence[Transaction]:
    if 'Posted Date,Reference Number,Payee,Address,Amount' not in lines[0]:
        raise Exception('Unrecognized file format for source: {source}')

    parsed_lines = list(csv.reader(lines))
    parsed_lines = parsed_lines[1:]
    return_data = []
    for row in parsed_lines:
        if len(row) < 5:
            raise Exception(
                f"Invalid number of cols for source: {source} data type: {BOA_CREDIT} cols: {len(row)}")

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


def parse_boadebit(lines, source) -> Sequence[Transaction]:
    parsed_lines = list(csv.reader(lines))

    starting_line = -1
    for i, row in enumerate(parsed_lines):
        if 'Beginning balance' in row[1]:
            starting_line = i + 1
            break
    if starting_line == -1:
        raise Exception(f'Could not find a starting line for {source}')

    parsed_lines = parsed_lines[starting_line:]
    return_data = []
    for row in parsed_lines:
        if len(row) < 3:
            raise Exception(
                f"Invalid number of cols for source: {source} data type: {BOA_DEBIT} cols: {len(row)}")

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
    files = [abspath(join(data_dir, f))
             for f in listdir(data_dir) if f[-4:] == ".csv"]
    for f in files:
        contents = ''
        with open(f, 'r') as fin:
            contents = fin.read()
        yield (f, contents)


# END DATA SOURCES

def validate_data_availability(datapath):
    return os.path.isdir(datapath)


def validate_all_data(datasource):
    errors = []
    output = ''
    for filepath, contents in datasource:
        try:
            parse_file(filepath, contents)
        except Exception as e:
            errors.append([filepath, contents, e])
            output += f"Error: {filepath}\n\tException:\n\t{str(e)}\n"
    if len(errors) > 0:
        output += f"Total errors: {len(errors)}\n"
    return (errors, output)


def parse_data_source(datasource) -> Sequence[Transaction]:
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
