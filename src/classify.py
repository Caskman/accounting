

def classify(transactions, rules):
    for transaction in transactions:
        # Run every rule on the transaction
        rule_results = [{"result": rule["run"](transaction), "rule": rule} for rule in rules]

        # Filter to the positive results
        positive_rule_results = list(filter(lambda r: r["result"], rule_results))

        # Set classification to the name of the first positive result
        if len(positive_rule_results) > 0:
            transaction.classification = positive_rule_results[0]["rule"]["name"]

        # Set the rest of the positive results as a lesser classification
        if len(positive_rule_results) > 1:
            lower_priority_rule_result_string = join_rule_result_names(positive_rule_results[1:])
            transaction.classification_debug = \
                f"Lesser classifications: {lower_priority_rule_result_string}"

def join_rule_result_names(rule_results):
    names = map(lambda r: r["rule"]["name"], rule_results)
    return ", ".join(names)


###############################################################################
# rule functions

# Matches on substring present in either the description or the source.
# Case insensitive
def rule_substring(rule_arg):
    rule_substring = rule_arg.lower()
    def rule_fn(transaction):
        return rule_substring in transaction.desc.lower() \
            or rule_substring in transaction.source.lower()
    return rule_fn

# Matches on the absolute value of the amount to two decimal places
def rule_abs_amt(rule_arg):
    rule_amt = _rule_abs_amt_format(rule_arg)
    def rule_fn(transaction):
        return _rule_abs_amt_format(transaction.amt) == rule_amt
    return rule_fn
def _rule_abs_amt_format(val):
    return "{:.2f}".format(abs(float(val)))
    
# substring-amt

# end rule functions
###############################################################################

# Declares rule functions that are available
rule_functions_map = {
    "substring": rule_substring,
    "abs-amt": rule_abs_amt,
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
    if len(rules_lines) == 0:
        raise Exception('Empty rules')
    rules_lines = map(lambda l: l.strip(), rules_lines)
    rules_lines = filter(lambda l: not (l == "" or (len(l)>0 and l[0]=='#')), rules_lines)

    # Convert strings into preliminary rule objects
    def convert_lines_to_bare_objs(line):
        columns = line.split('\t')
        name = columns[0]
        columns = columns[1:]
        return {
            "name": name,
            "columns": columns,
            "source": line,
        }
    bare_rule_objs = list(map(convert_lines_to_bare_objs, rules_lines))

    # Validating that rule args are even numbered
    for bare_rule_obj in bare_rule_objs:
        column_len = len(bare_rule_obj["columns"])
        if column_len == 0:
            source = bare_rule_obj["source"]
            raise Exception(f'Cannot have no components in a rule: {source}')
        if column_len % 2 != 0:
            raise Exception(f"Columns must be even numbered, getting {column_len}")
    
    # Extracting executable rule functions
    rule_objs = []
    for bare_rule_obj in bare_rule_objs:
        columns = bare_rule_obj["columns"]
        rule = {
            "name": bare_rule_obj["name"],
            "run": get_rule_function(columns)
        }
        rule_objs.append(rule)
    return rule_objs

if __name__ == '__main__':
    import sys
    # print(sys.argv)
    with open(sys.argv[1],'r') as fin:
        contents = fin.read()
        rules = process_rules(contents)
        print(rules)
