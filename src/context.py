import os

LOCAL_ENV_VARS_FILENAME = "local.env"
DOCKER_ENV_NAME = "DOCKERENV"

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
    if not DOCKER_ENV_NAME in os.environ:
        with open(LOCAL_ENV_VARS_FILENAME, "r") as fin:
            contents = fin.read()
        varobjs = parse_string_to_vars(contents)
        c.vars.extend(varobjs)
    return c

class Context():

    def __init__(self):
        self.vars = []

    def get_var(self, label):
        if label in os.environ:
            return os.getenv(label)
        else:
            found = list(filter(lambda x: x.label == label, self.vars))
            if len(found) < 1:
                raise Exception(f"Could not find var: {label}")
            return found[0].value

    def append_raw_vars(self, raw_vars):
        self.vars.extend(parse_string_to_vars(raw_vars))

    def __repl__(self):
        return f"{{ {self.vars} }}"
    def __str__(self):
        return self.__repl__()
    
class Var():
    def __init__(self, label, value):
        self.label = label
        self.value = value
