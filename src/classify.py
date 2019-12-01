

def classify(transactions, rules):
    for transaction in transactions:
        rule_results = [{"result": rule["run"](transaction), "rule": rule} for rule in rules]
        for rule_result in rule_results:
            if rule_result["result"]:
                transaction.classification = rule_result["rule"]["name"]
                break




###############################################################################
# rule functions

def substring(rule_args):
    rule_substring = rule_args['substring'].lower()
    def rule_fn(transaction):
        return rule_substring in transaction.desc.lower() \
            or rule_substring in transaction.label.lower()
    return rule_fn

# end rule functions
###############################################################################

# Easier to declare which column names correspond with which functions
# Makes it so we can just blindly grab functions that correspond with each column
# and then just remove dupes, which will happen when a function
# pulls args from multiple columns
rule_functions = [
    {
        "column_names": [ # these are the column names in the csv that will
                          # correspond with this rule function
            "substring"
        ],
        "function": substring,
    },
]

def convert_rule_functions_to_map():
    function_map = {}
    for rule_function in rule_functions:
        for column_name in rule_function["column_names"]:
            function_map[column_name] = rule_function["function"]
    return function_map
rule_functions_map = convert_rule_functions_to_map()

# Retrieves the rule function from the function map
def get_rule_function(name, args):
    if name in rule_functions_map:
        return rule_functions_map[name](args)
    else:
        raise Exception(f"could not find function name {name} in function map")

def mapify_rule_args(args):
    args_map = {}
    key = None
    for arg in args:
        if key:
            args_map[key] = arg
            key = None
        else:
            key = arg
    return args_map

# Converts a string into a list of rule objects
def process_rules(rules_string):
    rules_lines = rules_string.split('\n')
    rules_lines = rules_lines[1:]
    rules_lines = filter(lambda l: l.strip() != "", rules_lines)

    def convert_lines_to_bare_objs(line):
        columns = line.split('\t')
        name = columns[0]
        columns = columns[1:]
        return {
            "name": name,
            "columns": columns,
        }
    bare_rule_objs = list(map(convert_lines_to_bare_objs, rules_lines))

    for bare_rule_obj in bare_rule_objs:
        column_len = len(bare_rule_obj["columns"])
        if column_len % 2 != 0:
            raise Exception(f"Columns must be even numbered, getting {column_len}")
    
    rule_objs = []
    for bare_rule_obj in bare_rule_objs:
        columns = bare_rule_obj["columns"]
        args = {}
        args[columns[0]] = columns[1]
        rule = {
            "name": bare_rule_obj["name"],
            "args": mapify_rule_args(bare_rule_obj["columns"]),
            "run": get_rule_function(columns[0], args)
        }
        rule_objs.append(rule)
    return rule_objs
