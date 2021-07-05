import datetime
import classify
from typing import Sequence, Dict
from datainput import Transaction


ignored_class = ['Internal', 'Investments']
work_income_class = ['Income']
investment_class = ['Investments']


def group_sort_transactions(data_is, ix):
    # Group expenses
    group_keys = list(set(map(lambda i: ix(i).classification, data_is)))
    group_mapping = [[] for k in group_keys]
    for i in data_is:
        group_i = group_keys.index(ix(i).classification)
        group_mapping[group_i].append(i)

    # Calculate expense group sums
    group_sums = [sum(map(lambda i: ix(i).amt, group_mapping[eg_i]))
                  for eg_i, k in enumerate(group_keys)]

    # Sort expense groups by their totals
    group_sorted = sorted(range(len(group_keys)),
                          key=lambda eg_i: group_sums[eg_i])
    return [group_keys, group_sums, group_sorted]


def analyze_financial_data(data_is, ix):
    income = [i for i in data_is if ix(i).amt > 0]
    income_sum = sum(map(lambda i: ix(i).amt, income))

    # work income is a collection of classes
    work_income = [
        i for i in income if ix(i).classification in work_income_class]
    work_income_sum = sum(map(lambda i: ix(i).amt, work_income))

    # non work income is everything else
    non_work_income = [i for i in
                       income if not i in work_income]
    non_work_income_sum = sum(map(lambda i: ix(i).amt, non_work_income))
    income = Income(income, income_sum, work_income,
                    work_income_sum, non_work_income, non_work_income_sum)

    # expenses are less than 0
    expenses = [i for i in data_is if ix(i).amt < 0]
    expenses_sum = sum(map(lambda i: ix(i).amt, expenses))

    # group expenses by class, calculate sums, and sort
    [expense_group_keys, expense_group_sums,
        expense_group_sorted] = group_sort_transactions(expenses, ix)
    expenses_groups_coll = ExpenseGroupColl(
        expense_group_keys, expense_group_sums, expense_group_sorted)
    expenses = Expenses(expenses, expenses_sum, expenses_groups_coll)
    return (income, expenses)


def compile_data(data, rules):
    # Create a year cutoff
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    cutoff = datetime.datetime(year-1, month, 1).date()
    main_data = [t for t in data if t.date >= cutoff]
    def ix(i): return main_data[i]

    # Classify data
    classify.classify(main_data, rules)

    # Filter out internal trans
    wdata = list(
        filter(lambda i: not ix(i).classification in ignored_class, range(len(main_data))))

    # Breakdown into months

    # Group trans by month
    from typing import Dict
    months_dict: Dict[datetime.date, Month] = {}

    def months_key(date_obj):
        return datetime.datetime.strptime(f"{date_obj.year}-{date_obj.month}", "%Y-%m").date()
    for i in wdata:
        key = months_key(ix(i).date)
        if not key in months_dict:
            months_dict[key] = []
        month_list = months_dict[key]
        month_list.append(i)

    # Turn groups into Month objects and classify income vs expenses
    for month_key in months_dict.keys():
        i, e = analyze_financial_data(months_dict[month_key], ix)
        months_dict[month_key] = Month(month_key, i, e)

    total_i, total_e = analyze_financial_data(wdata, ix)
    investments = list(
        filter(lambda i: ix(i).classification in investment_class, range(len(main_data))))
    investments_sum = sum(map(lambda i: ix(i).amt, investments))
    year_finances = Year(cutoff, total_i, total_e,
                         investments, investments_sum)
    classified = [
        i for i in range(len(main_data)) if ix(i).classification != 'none']
    unclassified = [
        i for i in range(len(main_data)) if ix(i).classification == 'none']

    finances = Finances(main_data, year_finances,
                        months_dict, classified, unclassified)
    return finances


class Income():
    def __init__(self, income: Sequence[int], income_sum: int, workincome: Sequence[int], workincomesum: int, nonworkincome: Sequence[int], nonworkincomesum: int):
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
    def __init__(self, expenses: Sequence[int], expensessum: int, expensegroupcoll: ExpenseGroupColl):
        self.expenses = expenses
        self.expensessum = expensessum
        self.expensegroupcoll = expensegroupcoll


class Month():
    def __init__(self, date: datetime.date, income: Income, expense: Expenses):
        self.date = date
        self.income = income
        self.expense = expense


class Year():
    def __init__(self, cutoff_date: datetime.date, income: Income, expense: Expenses, investments: Sequence[int], investments_sum: int):
        self.cutoff_date = cutoff_date
        self.income = income
        self.expense = expense
        self.investments = investments
        self.investments_sum = investments_sum


class Finances():
    def __init__(self, source: Sequence[Transaction], year_finances: Year, month_finances: Dict[datetime.date, Month], classified: Sequence[int], unclassified: Sequence[int]):
        self.source = source
        self.year_finances = year_finances
        self.month_finances = month_finances
        self.classified = classified
        self.unclassified = unclassified

    def ix(self, i):
        return self.source[i]
