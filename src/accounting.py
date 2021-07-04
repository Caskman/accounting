from typing import Sequence, Dict
from datainput import Transaction
import datetime
import os

import s3datasource
import spreadsheet
import datainput
import classify

ignored_class = ['Internal', 'Investments']
work_income_class = ['Income']
investment_class = ['Investments']


def USD(val):
    return "{:.2f}".format(float(val))


def compile_data_into_spreadsheet():
    c = s3datasource.get_context()
    LOCAL_DATA_DIR = c.get_var("LOCAL_DATA_DIR")

    datasource = datainput.get_local_data_source(LOCAL_DATA_DIR)
    data = datainput.parse_data_source(datasource)

    run_id = c.get_run_id()
    outputpath = os.path.join(LOCAL_DATA_DIR, f"aaa-output-{run_id}.xlsx")

    spreadsheet.build_spreadsheet(c, data, outputpath)
    return outputpath


def group_sort_transactions(trans):
    # Group expenses
    group_keys = list(set(map(lambda t: t.classification, trans)))
    group_mapping = [[] for k in group_keys]
    for t_i, t in enumerate(trans):
        group_i = group_keys.index(t.classification)
        group_mapping[group_i].append(t_i)

    # Calculate expense group sums
    group_sums = [sum(map(lambda t_i: trans[t_i].amt, group_mapping[eg_i]))
                  for eg_i, k in enumerate(group_keys)]

    # Sort expense groups by their totals
    group_sorted = sorted(range(len(group_keys)),
                          key=lambda eg_i: group_sums[eg_i])
    return [group_keys, group_sums, group_sorted]


def pull(src, indices):
    return [src[i] for i in indices]


def analyze_financial_data(transaction_data):
    income = [t for t in transaction_data if t.amt > 0]
    income_sum = sum(map(lambda t: t.amt, income))

    # work income is a collection of classes
    work_income = [
        t_i for t_i, t in enumerate(income) if t.classification in work_income_class]
    work_income_sum = sum(map(lambda i: income[i].amt, work_income))

    # non work income is everything else
    non_work_income = [t_i for t_i, t in enumerate(
        income) if not t_i in work_income]
    non_work_income_sum = sum(map(lambda i: income[i].amt, non_work_income))
    income = Income(income, income_sum, work_income,
                    work_income_sum, non_work_income, non_work_income_sum)

    # expenses are less than 0
    expenses = [t for t in transaction_data if t.amt < 0]
    expenses_sum = sum(map(lambda t: t.amt, expenses))

    # group expenses by class, calculate sums, and sort
    [expense_group_keys, expense_group_sums,
        expense_group_sorted] = group_sort_transactions(expenses)
    expenses_groups_coll = ExpenseGroupColl(
        expense_group_keys, expense_group_sums, expense_group_sorted)
    expenses = Expenses(expenses, expenses_sum, expenses_groups_coll)
    return (income, expenses)


def compile_data():
    c = s3datasource.get_context()
    LOCAL_DATA_DIR = c.get_var("LOCAL_DATA_DIR")

    # Load data
    datasource = datainput.get_local_data_source(LOCAL_DATA_DIR)
    data = datainput.parse_data_source(datasource)

    # Create a year cutoff
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    cutoff = datetime.datetime(year-1, month, 1).date()
    last_years_data = [t for t in data if t.date >= cutoff]

    # Load classification rules
    rules_contents = None
    with open('classification_rules.csv', 'r') as fin:
        rules_contents = fin.read()
    rules = classify.process_rules(rules_contents)

    # Classify data
    classify.classify(last_years_data, rules)

    # Filter out internal trans
    whole_data = last_years_data
    wdata = list(
        filter(lambda t: not t.classification in ignored_class, whole_data))

    # Breakdown into months

    # Group trans by month
    from typing import Dict
    months_dict: Dict[datetime.date, Month] = {}

    def months_key(date_obj):
        return datetime.datetime.strptime(f"{date_obj.year}-{date_obj.month}", "%Y-%m").date()
    for t in wdata:
        key = months_key(t.date)
        if not key in months_dict:
            months_dict[key] = []
        month_list = months_dict[key]
        month_list.append(t)

    # Turn groups into Month objects and classify income vs expenses
    for month_key in months_dict.keys():
        i, e = analyze_financial_data(months_dict[month_key])
        months_dict[month_key] = Month(month_key, i, e)

        # transaction_data = months_dict[month_key]
        # # positive amounts are income
        # income = [t for t in transaction_data if t.amt > 0]
        # income_sum = sum(map(lambda t: t.amt,income))

        # # work income is a collection of classes
        # work_income = [
        #     t_i for t_i, t in enumerate(income) if t.classification in work_income_class]
        # work_income_sum = sum(map(lambda i: income[i].amt,work_income))

        # # non work income is everything else
        # non_work_income = [t_i for t_i,t in enumerate(income) if not t_i in work_income]
        # non_work_income_sum = sum(map(lambda i: income[i].amt,non_work_income))
        # income = Income(income, income_sum,work_income,work_income_sum, non_work_income,non_work_income_sum)

        # # expenses are less than 0
        # expenses = [t for t in transaction_data if t.amt < 0]
        # expenses_sum = sum(map(lambda t: t.amt,expenses))

        # # group expenses by class, calculate sums, and sort
        # [expense_group_keys, expense_group_sums,
        #     expense_group_sorted] = group_sort_transactions(expenses)
        # expenses_groups_coll = ExpenseGroupColl(expense_group_keys, expense_group_sums, expense_group_sorted)
        # expenses = Expenses(expenses,expenses_sum, expenses_groups_coll)

        # months_dict[month_key] = Month(month_key, income, expenses)

    # Print out month by month results

    # prints the top five trans by absolute dollar amount

    def printTop5(trans: Sequence[Transaction]):
        for t in sorted(trans, key=lambda t: abs(float(t.amt)), reverse=True)[:5]:
            print(f"\t{float(t.amt)}\t{t.classification}\t{t.desc}")

    # Sort the month keys and print in month order
    sorted_month_keys = sorted(months_dict.keys())
    for month_key in sorted_month_keys:
        month_obj = months_dict[month_key]

        # # identify work income separate from other income
        # work_income = [
        #     t for t in month_obj.income if t.classification in work_income_class]
        # non_work_income = [t for t in month_obj.income if not t in work_income]

        # [expense_group_keys, expense_group_sums,
        #     expense_group_sorted] = group_sort_transactions(month_obj.expense)

        print(str(month_key))
        print(
            f"Income: {USD(month_obj.income.income_sum)}")
        print(
            f"\tWork income: {USD(month_obj.income.workincomesum)}")
        printTop5(pull(month_obj.income.income,
                  month_obj.income.nonworkincome))
        print(
            f"Expenses: {USD(month_obj.expense.expensessum)}")
        print(f"Top expenses:")
        printTop5(month_obj.expense.expenses)
        print(f"Top expense groups:")
        egc = month_obj.expense.expensegroupcoll
        for eg_i in egc.group_sums_sorted[:5]:
            print(
                f"\t{egc.group_keys[eg_i]}\t{USD(egc.group_sums[eg_i])}")
        print()

    # Print out 12-month report
    total_i, total_e = analyze_financial_data(wdata)
    investments = list(
        filter(lambda t: t.classification in investment_class, whole_data))
    investments_sum = sum(map(lambda t: t.amt, investments))
    year_finances = Year(cutoff, total_i, total_e,
                         investments, investments_sum)
    finances = Finances(year_finances, months_dict)

    # income = [t for t in wdata if t.amt > 0]
    # expenses = [t for t in wdata if t.amt < 0]

    # # Calculate expense groups
    # [expense_group_keys, expense_group_sums,
    #     expense_group_sorted] = group_sort_transactions(expenses)

    print()
    print(f"Since {finances.year_finances.cutoff_date}:")
    print(f"Income: {USD(finances.year_finances.income.income_sum)}")
    print(f"Expenses: {USD(finances.year_finances.expense.expensessum)}")
    print(f"Investments: {USD(finances.year_finances.investments_sum)}")
    print(f"Biggest Expense Groups:")
    egc = finances.year_finances.expense.expensegroupcoll
    for eg_i in egc.group_sums_sorted[:20]:
        print(
            f"\t{egc.group_keys[eg_i]}\t{USD(egc.group_sums[eg_i])}")

    # Print out unclassified data if any
    classified_data = [
        t for t in last_years_data if t.classification != 'none']
    unclassified_data = [
        t for t in last_years_data if t.classification == 'none']

    if len(unclassified_data) > 0:
        for t in unclassified_data:
            print(str(t))

        print(f"classified {len(list(classified_data))}")
        print(f"unclassified {len(list(unclassified_data))}")
        print(f"total data {len(list(last_years_data))}")


class Income():
    def __init__(self, income: Sequence[Transaction], income_sum: int, workincome: Sequence[int], workincomesum: int, nonworkincome: Sequence[int], nonworkincomesum: int):
        self.income = income
        self.income_sum = income_sum
        self.workincome = workincome
        self.workincomesum = workincomesum
        self.nonworkincome = nonworkincome
        self.nonworkincomesum = nonworkincomesum


class ExpenseGroupColl():
    def __init__(self, group_keys: Sequence[str], group_sums: Sequence[int], group_sums_sorted: Sequence[int]):
        self.group_keys = group_keys
        self.group_sums = group_sums
        self.group_sums_sorted = group_sums_sorted


class Expenses():
    def __init__(self, expenses: Sequence[Transaction], expensessum: int, expensegroupcoll: ExpenseGroupColl):
        self.expenses = expenses
        self.expensessum = expensessum
        self.expensegroupcoll = expensegroupcoll


class Month():
    def __init__(self, date: datetime.date, income: Income, expense: Expenses):
        self.date = date
        self.income = income
        self.expense = expense


class Year():
    def __init__(self, cutoff_date: datetime.date, income: Income, expense: Expenses, investments: Sequence[Transaction], investments_sum: int):
        self.cutoff_date = cutoff_date
        self.income = income
        self.expense = expense
        self.investments = investments
        self.investments_sum = investments_sum


class Finances():
    def __init__(self, year_finances: Year, month_finances: Dict[datetime.date, Month]):
        self.year_finances = year_finances
        self.month_finances = month_finances


if __name__ == "__main__":
    compile_data()
