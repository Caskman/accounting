from datetime import datetime
import os
from time import time

LOCAL_ENV_VARS_FILENAME = "local.env"
DOCKER_ENV_NAME = "DOCKERENV"
LOCAL_DATA_DIR = 'local_data/'

def parse_string_to_vars(text):
    lines = text.split("\n")
    lines = [l.strip() for l in lines]
    lines = [l for l in lines if l != ""]
    var_objs = []
    for l in lines:
        splits = l.split("=")
        var_objs.append(Var(splits[0], splits[1]))
    return var_objs

def init_context():
    c = Context()
    contents = []
    if os.path.isfile(LOCAL_ENV_VARS_FILENAME):
        with open(LOCAL_ENV_VARS_FILENAME, "r") as fin:
            contents = fin.read()
        varobjs = parse_string_to_vars(contents)
        c.vars.extend(varobjs)
    append_additional_vars(c)
    return c

def append_additional_vars(c):
    c.vars.append(Var("LOCAL_DATA_DIR", LOCAL_DATA_DIR))

class Context():

    def __init__(self):
        self.vars = []

    def get_var(self, label):
        if label in os.environ:
            return os.getenv(label)
        else:
            found = list(filter(lambda x: x.label == label, self.vars))
            if len(found) < 1:
                default_value = self.get_default_var(label)
                if not default_value:
                    raise Exception(f"Could not find var: {label}")
                return default_value
            return found[0].value

    def get_default_var(self, label):
        var_map = {
            'CONFIG_PATH': 'config.txt',
            'IN_AWS_LAMBDA': 'false',
        }
        if label in var_map:
            return var_map[label]
        else:
            return None

    def append_raw_vars(self, raw_vars):
        self.vars.extend(parse_string_to_vars(raw_vars))
    
    def get_run_id(self):
        return int(time())

    def __repl__(self):
        return f"{{ {self.vars} }}"
    def __str__(self):
        return self.__repl__()
    
class Var():
    def __init__(self, label, value):
        self.label = label
        self.value = value
