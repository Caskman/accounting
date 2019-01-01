from os import listdir, rename
from os.path import join, abspath
from re import match, search

CSV_DIR = "csv"

class FileObj():
    def __init__(self, type, label, date):
        self.type = type
        self.label = label
        self.date = date
    def __repl__(self):
        return f"{{ {self.label}, {self.type}, {self.date} }}"
    def __str__(self):
        return self.__repl__()

def current_format_parse(f):
    m = search(r"(\w+)_(\w+)_(\w+)\.csv", f)
    try:
        f_type = m.group(2)
        date = m.group(3)
        label = m.group(1)
        return FileObj(f_type, label, date)
    except AttributeError:
        raise Exception(f"Filename {f} missing components")

files = [f for f in listdir(CSV_DIR) if f[-4:] == ".csv"]

for filename in files:
    comps = current_format_parse(filename)
    if comps.label != "something":
        filepath = abspath(join(CSV_DIR, filename))
        new_filename = f"{comps.label}_{comps.type}_{comps.date}.csv"
        new_filepath = abspath(join(CSV_DIR, new_filename))
        # rename(filepath, new_filepath)
        print(f"{filename} -> {new_filename}")

