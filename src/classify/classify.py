from typing import Sequence

from datainput import Transaction


def classify(transactions, rules):
    for transaction in transactions:
        # Run every rule on the transaction
        rule_results = [{"result": rule["run"](
            transaction), "rule": rule} for rule in rules]

        # Filter to the positive results
        positive_rule_results = list(
            filter(lambda r: r["result"], rule_results))

        # Set classification to the name of the first positive result
        if len(positive_rule_results) > 0:
            transaction.classification = positive_rule_results[0]["rule"]["name"]

        # Set the rest of the positive results as a lesser classification
        if len(positive_rule_results) > 1:
            lower_priority_rule_result_string = join_rule_result_names(
                positive_rule_results[1:])
            transaction.classification_debug = \
                f"Lesser classifications: {lower_priority_rule_result_string}"


def join_rule_result_names(rule_results):
    names = map(lambda r: r["rule"]["name"], rule_results)
    return ", ".join(names)


def validate_classifications(trans: Sequence[Transaction]):
    error = False
    # Check for unclassified data
    classified = [
        i for i, t in enumerate(trans) if t.classification != 'none']
    unclassified = [
        i for i, t in enumerate(trans) if t.classification == 'none']
    error = error or len(unclassified) > 0

    # Check that returns are positive
    negative_returns = [i for i, t in enumerate(
        trans) if t.classification == "Returns" and t.amt < 0]
    error = error or len(negative_returns) > 0

    return ClassificationErrors(error, classified, unclassified, negative_returns)


class ClassificationErrors:
    def __init__(self, classification_error: bool, classified_trans: Sequence[int], unclassified_trans: Sequence[int], negative_returns: Sequence[int]):
        self.classification_error = classification_error
        self.classified_trans = classified_trans
        self.unclassified_trans = unclassified_trans
        self.negative_returns = negative_returns
