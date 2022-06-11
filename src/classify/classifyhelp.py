from analyze import standard_compilation
import console
from classify import yaml


def show_classification_help(show_classification_categories):
    if show_classification_categories:
        rules_contents = yaml.get_rules_string()
        rules = yaml.process_rules(rules_contents)
        names = sorted(list(set(map(lambda r: r['name'], rules))))

        output = "\n".join(names)
        print(output)
    else:
        finances = standard_compilation(12)

        console.print_classification_errors(finances)
