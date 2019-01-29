
def get_var(var_name):
    contents = []
    with open("local.env", "r") as fin:
        contents = fin.read()
    lines = contents.split("\n")
    lines = [l.strip() for l in lines]
    lines = [l for l in lines if l != ""]
    env_vars = []
    for l in lines:
        splits = l.split("=")
        env_vars.append(Var(splits[0], splits[1]))
    found = list(filter(lambda x: x.label == var_name, env_vars))
    if len(found) < 1:
        raise Exception(f"Could not find var: {var_name}")
    return found[0].value

class Var():
    def __init__(self, label, value):
        self.label = label
        self.value = value
