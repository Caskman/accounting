from re import sub
import yaml
from typing import Sequence, Union, Dict, Any
import datetime
from util import parse_decimal
import paths

from datainput import Transaction

# Class Definitions


class RuleStatement:
    type: str = None
    params: Dict[str, Any] = None

    def __init__(self, yaml_obj):
        if 'type' not in yaml_obj:
            raise Exception(
                'RuleStatement yaml object does not contains key "type"')
        self.type = yaml_obj['type']
        if 'params' not in yaml_obj:
            raise Exception(
                'RuleStatement yaml object does not contains key "params"')
        self.params = yaml_obj['params']


class Rule:
    name: str
    statements: Sequence[RuleStatement]
    description: str

    def __init__(self, yaml_obj):
        if 'name' not in yaml_obj:
            raise RuleObjTypeException(
                'Rule yaml object does not contains key "name"')
        self.name = yaml_obj['name']
        if 'statements' not in yaml_obj:
            raise RuleObjTypeException(
                'Rule yaml object does not contains key "statements"')
        self.statements = list(map(lambda o: RuleStatement(o),
                                   yaml_obj['statements']))
        self.description = yaml_obj['description'] if 'description' in yaml_obj else ''


class RuleGroup:
    description: str
    rules: Sequence[Rule]

    def __init__(self, yaml_obj):
        if 'description' not in yaml_obj:
            raise RuleGroupObjTypeException(
                'RuleGroup yaml object does not contains key "description"')
        self.description = yaml_obj['description']
        if 'rules' not in yaml_obj:
            raise RuleGroupObjTypeException(
                'RuleGroup yaml object does not contains key "rules"')
        self.rules = list(map(lambda o: Rule(o), yaml_obj['rules']))


class Rules:
    rules: Sequence[Union[Rule, RuleGroup]]

    def __init__(self, yaml_obj=None, rules: Sequence[Rule] = None):
        if rules:
            self.rules = rules
        else:
            if 'rules' not in yaml_obj:
                raise Exception(
                    'Rules yaml object does not contains key "rules"')
            self.rules = []
            for obj in yaml_obj['rules']:
                specific_error = False
                try:
                    rule_obj = Rule(obj)
                except RuleObjTypeException as err:
                    specific_error = err
                try:
                    rule_obj = RuleGroup(obj)
                except RuleGroupObjTypeException as err:
                    specific_error = err

                if rule_obj:
                    self.rules.append(rule_obj)
                elif specific_error:
                    raise specific_error
                else:
                    raise Exception(
                        'Something has gone horribly wrong in yaml parsing')


class RuleObjTypeException(Exception):
    pass


class RuleGroupObjTypeException(Exception):
    pass

# Function Definitions


def process_rules(rules_string):
    rules = convert_to_rules(rules_string)
    rules = flatten_rules(rules)
    rules_objs = convert_to_rule_objs(rules)

    return rules_objs


def convert_to_rules(rules_string: str):
    yaml_obj = yaml.load(rules_string, Loader=yaml.FullLoader)
    rules = Rules(yaml_obj)
    return rules


def flatten_rules(rules: Rules):
    rules_seq = []
    for instance in rules.rules:
        if isinstance(instance, Rule):
            rules_seq.append(instance)
        elif isinstance(instance, RuleGroup):
            for sub_instance in instance.rules:
                rules_seq.append(sub_instance)
        else:
            raise Exception(
                'Unrecognizable rule instance when flattening instances')
    rules_seq = Rules(rules=rules_seq)
    return rules_seq

# Statement Validators


def substring_validator(statement: RuleStatement):
    if 'string' not in statement.params:
        raise Exception(
            'Rule validation failed: substring statement has no string param')
    if not isinstance(statement.params['string'], str):
        raise Exception(
            'Rule validation failed: string param is not of type str')
    return True


def abs_amt_validator(statement: RuleStatement):
    if 'amt' not in statement.params:
        raise Exception(
            'Rule validation failed: abs-amt statement has no amt param')
    amt_param = statement.params['amt']
    try:
        parse_decimal(str(amt_param))
    except Exception as e:
        raise Exception(
            f'Rule validation failed: amt param <{amt_param}> is not a Decimal') from e
    return True


def date_validator(statement: RuleStatement):
    if 'date' not in statement.params:
        raise Exception(
            'Rule validation failed: date statement has no date param')
    date_param = statement.params['date']
    if not isinstance(date_param, datetime.date):
        try:
            datetime.datetime.strptime(str(date_param), '%Y-%m-%d').date()
        except ValueError as e:
            error_message = f'Rule validation failed: date statement date param <{date_param}> is not of format YYYY-MM-DD'
            raise Exception(error_message) from e
    return True


statement_validators = {
    'substring': substring_validator,
    'abs-amt': abs_amt_validator,
    'date': date_validator,
}

# Statement Executors


def substring_executor(params):
    substring = params['string'].lower()

    def resolve(transaction: Transaction):
        return substring in transaction.desc.lower() or substring in transaction.source.lower()
    return resolve


def abs_amt_executor(params):
    amt = _rule_abs_amt_format(params['amt'])

    def resolve(transaction: Transaction):
        return _rule_abs_amt_format(transaction.amt) == amt
    return resolve


def _rule_abs_amt_format(val):
    return "{:.2f}".format(abs(float(val)))


def date_executor(params):
    if isinstance(params['date'], datetime.date):
        date = params['date']
    else:
        date = datetime.datetime.strptime(params['date'], '%Y-%m-%d')

    def resolve(transaction: Transaction):
        return transaction.date.strftime('%Y-%m-%d') == date.strftime('%Y-%m-%d')
    return resolve


statement_executors = {
    'substring': substring_executor,
    'abs-amt': abs_amt_executor,
    'date': date_executor,
}

## Assembling & Validation


def convert_to_rule_objs(rules: Rules):
    rule_objs = []
    for rule in rules.rules:
        if validate_rule(rule):
            rule_obj = {
                "name": rule.name,
                "run": get_statement_functions(rule.statements),
                "source": rule,
            }
            rule_objs.append(rule_obj)
        else:
            raise Exception('Rule validation failed')
    return rule_objs


def get_statement_functions(statements: Sequence[RuleStatement]):
    functions = []
    for statement in statements:
        function = statement_executors[statement.type](statement.params)
        functions.append(function)

    def resolve(transaction: Transaction):
        for function in functions:
            if not function(transaction):
                return False
        return True
    return resolve


def validate_rule(rule: Union[Rule, RuleGroup]):
    if isinstance(rule, Rule):
        if (not rule.name) or rule.name.strip() == '':
            raise Exception(
                'Rule validation failed: rule name is empty or nonexistent')
        if not rule.statements:
            raise Exception(
                'Rule validation failed: rule does not have statements')
        if len(rule.statements) < 1:
            raise Exception(
                'Rule validation failed: rule has empty statements')

        for statement in rule.statements:
            if (not statement.type) or statement.type.strip() == '':
                raise Exception(
                    'Rule validation failed: statement has no type')
            if not statement.params:
                raise Exception(
                    'Rule validation failed: statement has no params')

            if statement.type not in statement_validators:
                raise Exception(
                    f'Rule validation failed: statement type not recognized <{statement.type}>')
            statement_validators[statement.type](statement)
        return True

    else:
        raise Exception('Rule validation failed: rule is not of type Rule')


def get_rules_string(context):
    rules_contents = None
    rules_file_path = paths.get_classification_rules_file_path(context)
    with open(rules_file_path, 'r') as fin:
        rules_contents = fin.read()
    return rules_contents
