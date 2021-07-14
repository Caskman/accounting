from dateutil.relativedelta import relativedelta
from copy import copy
import datetime
from decimal import Decimal
import classify
from typing import Callable, Sequence, Dict
from datainput import Transaction


ignored_class = ['Internal', 'Investments']
work_income_class = ['Income']
investment_class = ['Investments']
returns_class = ['Returns']


def group_sort_transactions(data_is: Sequence[int], ix: Callable[[int], Transaction]):
    # Calculate total sum
    total_sum = sum(map(lambda i: abs(ix(i).amt), data_is))

    # Group transactions
    group_keys = list(set(map(lambda i: ix(i).classification, data_is)))
    group_mapping = [[] for k in group_keys]
    for i in data_is:
        group_i = group_keys.index(ix(i).classification)
        group_mapping[group_i].append(i)

    # Calculate transaction group sums
    group_sums = [sum(map(lambda i: ix(i).amt, group_mapping[eg_i]))
                  for eg_i, k in enumerate(group_keys)]

    # Calculate group percentages
    group_percentages = [
        abs(group_sums[i])/total_sum for i in range(len(group_keys))]

    # Sort expense groups by their totals
    group_sorted = sorted(range(len(group_keys)),
                          key=lambda eg_i: group_sums[eg_i])
    return [group_keys, group_sums, group_percentages, group_sorted]


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

    # returns income is non work income that is a refund
    returns_income = [
        i for i in income if ix(i).classification in returns_class]
    returns_income_sum = sum(map(lambda i: ix(i).amt, returns_income))

    income = Income(income, income_sum, work_income,
                    work_income_sum, non_work_income, non_work_income_sum, returns_income, returns_income_sum)

    # expenses are less than 0
    expenses = [i for i in data_is if ix(i).amt < 0]
    expenses_sum = sum(map(lambda i: ix(i).amt, expenses))

    # group expenses by class, calculate sums, and sort
    [expense_group_keys, expense_group_sums, expense_group_percentages,
        expense_group_sorted] = group_sort_transactions(expenses, ix)
    expenses_groups_coll = ExpenseGroupColl(
        expense_group_keys, expense_group_sums, expense_group_percentages, expense_group_sorted)
    expenses = Expenses(expenses, expenses_sum, expenses_groups_coll)

    amount_saved = abs(income_sum) - abs(expenses_sum)
    saving_ratio = amount_saved / abs(income_sum)
    savings_goals = [Decimal(0.05*step) for step in range(11)]
    savings_goal_amts = [goal*income_sum for goal in savings_goals]
    savings_goal_leftover = [amount_saved -
                             goal_amt for goal_amt in savings_goal_amts]

    savings = Savings(amount_saved, saving_ratio, savings_goals,
                      savings_goal_amts, savings_goal_leftover)

    return (income, expenses, savings)


def get_date_years_ago(years: int):
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    return datetime.datetime(year-years, month, 1).date()


def get_date_months_ago(months: int):
    now = datetime.datetime.now()
    thismonth = datetime.datetime(now.year, now.month, 1).date()
    monthsago = thismonth - relativedelta(months=months)
    return datetime.datetime(monthsago.year, monthsago.month, 1).date()


def compile_data(data: Sequence[Transaction], rules, cutoff_date: datetime.date):
    main_data = [t for t in data if t.date >= cutoff_date]
    def ix(i): return main_data[i]

    # Classify data
    classify.classify(main_data, rules)

    # Validate classified data
    class_errors = classify.validate_classifications(main_data)

    # Filter out internal trans
    wdata = list(
        filter(lambda i: not ix(i).classification in ignored_class, range(len(main_data))))

    # Breakdown into months

    # Group trans by month
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
        income, expenses, savings = analyze_financial_data(
            months_dict[month_key], ix)
        months_dict[month_key] = Month(month_key, income, expenses, savings)

    # Compile data on the whole period
    total_income, total_expenses, gross_savings = analyze_financial_data(
        wdata, ix)
    investments = list(
        filter(lambda i: ix(i).classification in investment_class, range(len(main_data))))
    investments_sum = sum(map(lambda i: ix(i).amt, investments))

    # Calculate how many months the data covers
    min_date = min(map(lambda t: t.date, main_data))
    max_date = max(map(lambda t: t.date, main_data))
    whole_period_days = (max_date - min_date).days
    whole_period_months = round(whole_period_days / 30)

    # Create avg month savings object
    avg_month_amount_saved = gross_savings.amount_saved / whole_period_months
    avg_month_savings_goals = copy(gross_savings.savings_goals)
    avg_month_savings_goal_amts = [
        a/whole_period_months for a in gross_savings.savings_goal_amts]
    avg_month_savings_goal_leftover = [
        a/whole_period_months for a in gross_savings.savings_goal_leftover]
    avg_month_savings = Savings(avg_month_amount_saved, gross_savings.saving_ratio,
                                avg_month_savings_goals, avg_month_savings_goal_amts, avg_month_savings_goal_leftover)

    whole_period_finances = WholePeriod(cutoff_date, whole_period_months, total_income, total_expenses, gross_savings, avg_month_savings,
                                        investments, investments_sum)

    # Create final Finances object
    ignored_transactions = [i for i in range(len(main_data)) if i not in wdata]
    finances = Finances(main_data, whole_period_finances,
                        months_dict, ignored_transactions, class_errors)
    return finances


class Income():
    def __init__(self, income: Sequence[int], income_sum: int, workincome: Sequence[int], workincomesum: int, nonworkincome: Sequence[int], nonworkincomesum: int, returnsincome: Sequence[int], returnsincomesum: int):
        self.income = income
        self.income_sum = income_sum
        self.workincome = workincome
        self.workincomesum = workincomesum
        self.nonworkincome = nonworkincome
        self.nonworkincomesum = nonworkincomesum
        self.returnsincome = returnsincome
        self.returnsincomesum = returnsincomesum


class ExpenseGroupColl():
    def __init__(self, group_keys: Sequence[str], group_sums: Sequence[int], group_percentages: Sequence[float], group_sums_sorted: Sequence[int]):
        self.group_keys = group_keys
        self.group_sums = group_sums
        self.group_percentages = group_percentages
        self.group_sums_sorted = group_sums_sorted


class Expenses():
    def __init__(self, expenses: Sequence[int], expensessum: int, expensegroupcoll: ExpenseGroupColl):
        self.expenses = expenses
        self.expensessum = expensessum
        self.expensegroupcoll = expensegroupcoll


class Savings():
    def __init__(self, amount_saved: float, saving_ratio: float, savings_goals: Sequence[float], savings_goal_amts: Sequence[float], savings_goal_leftover: Sequence[float]):
        self.amount_saved = amount_saved
        self.saving_ratio = saving_ratio
        self.savings_goals = savings_goals
        self.savings_goal_amts = savings_goal_amts
        self.savings_goal_leftover = savings_goal_leftover


class Month():
    def __init__(self, date: datetime.date, income: Income, expense: Expenses, savings: Savings):
        self.date = date
        self.income = income
        self.expense = expense
        self.savings = savings


class WholePeriod():
    def __init__(self, cutoff_date: datetime.date, period_in_months: int, income: Income, expense: Expenses, gross_savings: Savings, avg_monthly_savings: Savings, investments: Sequence[int], investments_sum: int):
        self.cutoff_date = cutoff_date
        self.period_in_months = period_in_months
        self.income = income
        self.expense = expense
        self.gross_savings = gross_savings
        self.avg_monthly_savings = avg_monthly_savings
        self.investments = investments
        self.investments_sum = investments_sum


class Finances():
    def __init__(self, source: Sequence[Transaction], whole_finances: WholePeriod, monthly_finances: Dict[datetime.date, Month], ignored: Sequence[int], classification_errors: classify.ClassificationErrors):
        self.source = source
        self.whole_finances = whole_finances
        self.monthly_finances = monthly_finances
        self.ignored = ignored
        self.classification_errors = classification_errors

    def ix(self, i):
        return self.source[i]
