

def classify(transactions, rules):
    for transaction in transactions:
        rule_results = [{"result": rule["run"](transaction), "rule": rule} for rule in rules]
        positive_rule_results = list(filter(lambda r: r["result"], rule_results))
        if len(positive_rule_results) > 0:
            transaction.classification = positive_rule_results[0]["rule"]["name"]
        if len(positive_rule_results) > 1:
            lower_priority_rule_result_string = join_rule_result_names(positive_rule_results[1:])
            transaction.classification_debug = \
                f"Lower priority rule results: {lower_priority_rule_result_string}"

def join_rule_result_names(rule_results):
    names = map(lambda r: r["rule"]["name"], rule_results)
    return ", ".join(names)


###############################################################################
# rule functions

def rule_substring(rule_arg):
    rule_substring = rule_arg.lower()
    def rule_fn(transaction):
        return rule_substring in transaction.desc.lower() \
            or rule_substring in transaction.label.lower()
    return rule_fn

# end rule functions
###############################################################################

# Declares rule functions that are available
rule_functions_map = {
    "substring": rule_substring
}

# Retrieves the rule function from the function map
def get_rule_function(fields):
    pairs = pairify_fields(fields)
    functions = []
    for pair in pairs:
        if not pair[0] in rule_functions_map:
            raise Exception(f"Could not find function {pair[0]} in function map")
        function = rule_functions_map[pair[0]](pair[1])
        functions.append(function)
    def resolve(transaction):
        for function in functions:
            if not function(transaction):
                return False
        return True
    return resolve

def pairify_fields(fields):
    field_list = []
    first = None
    for field in fields:
        if first:
            field_list.append([first, field])
            first = None
        else:
            first = field
    return field_list

# Converts a string into a list of rule objects
def process_rules(rules_string):
    rules_lines = rules_string.split('\n')
    rules_lines = rules_lines[1:]
    rules_lines = map(lambda l: l.strip(), rules_lines)
    rules_lines = filter(lambda l: l != "", rules_lines)

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
        rule = {
            "name": bare_rule_obj["name"],
            "run": get_rule_function(columns)
        }
        rule_objs.append(rule)
    return rule_objs
