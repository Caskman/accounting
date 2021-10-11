import s3datasource
from classify import custom as custom_classify, yaml as yaml_classify
import yaml
import json
import datainput
import compile
import console


def convert():
    c = s3datasource.get_context()
    LOCAL_DATA_DIR = c.get_var("LOCAL_DATA_DIR")

    rules_contents = None
    with open('classification_rules.csv', 'r') as fin:
        rules_contents = fin.read()
    rules_custom = custom_classify.process_rules(rules_contents)

    yaml_obj = {"rules": []}
    for rule in rules_custom:
        rule_obj = {
            "name": rule['name'],
            "statements": [],
        }
        for pair in custom_classify.pairify_fields(rule['bare_rule_obj']['columns']):
            stmt_name = pair[0]
            stmt_obj = {
                "type": stmt_name,
                "params": {},
            }
            if stmt_name == 'substring':
                stmt_obj['params']['string'] = pair[1]
            elif stmt_name == 'abs-amt':
                stmt_obj['params']['amt'] = int(pair[1])
            else:
                raise Exception(f'what kind of rule is {stmt_name}')
            rule_obj['statements'].append(stmt_obj)
        yaml_obj['rules'].append(rule_obj)

    yaml_output = yaml.dump(yaml_obj, sort_keys=False,
                            default_flow_style=False, Dumper=MyDumper)
    with open('classification_rules_test.yaml', 'w') as fout:
        fout.write(yaml_output)


def test():
    with open('classification_rules_example.yaml', 'r') as fin:
        document = fin.read()
    print(json.dumps(yaml.load(document), indent=4))


def test2():
    c = s3datasource.get_context()
    LOCAL_DATA_DIR = c.get_var("LOCAL_DATA_DIR")

    # Load data
    datasource = datainput.get_local_data_source(LOCAL_DATA_DIR)
    data_all_time = datainput.parse_data_source(datasource)

    # Load both sets of rules
    with open('classification_rules_candidate.yaml', 'r') as fin:
        rules_string_yaml = fin.read()
    with open('classification_rules.csv', 'r') as fin:
        rules_string_custom = fin.read()

    rules_custom = custom_classify.process_rules(rules_string_custom)
    rules_yaml = yaml_classify.process_rules(rules_string_yaml)

    finances_custom = compile.compile_data(
        data_all_time, rules_custom, compile.get_date_months_ago(12))
    finances_yaml = compile.compile_data(
        data_all_time, rules_yaml, compile.get_date_months_ago(12))

    print(finances_custom == finances_yaml)

    console.console_print_summary(finances_yaml)


class MyDumper(yaml.Dumper):

    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)


if __name__ == '__main__':
    # convert()
    # test()
    test2()
