from typing import Sequence
from compile import Finances
from util import percent, USD

# prints the top five trans by absolute dollar amount


def print_top(data_is: Sequence[int], f, n=5):
    for i in sorted(data_is, key=lambda i: abs(float(f.ix(i).amt)), reverse=True)[:n]:
        t = f.ix(i)
        print(f"\t{USD(t.amt)}\t{t.classification}\t{t.desc}")


def print_classification_errors(finances: Finances):
    f = finances
    # Print out classification errors
    if finances.classification_errors.classification_error:
        print(f"=====Classification Error=====")
        class_warnings = finances.classification_errors
        if len(class_warnings.unclassified_trans) > 0:
            print("Unclassified Transactions")
            for i in class_warnings.unclassified_trans:
                print(str(f.ix(i)))

            print(f"classified {len(class_warnings.classified_trans)}")
            print(f"unclassified {len(class_warnings.unclassified_trans)}")
            print(f"total data {len(finances.source)}")
            print()

        if len(class_warnings.negative_returns) > 0:
            print("Negative Returns Present")
            for i in class_warnings.negative_returns:
                print(str(f.ix(i)))

        print(f"=====Classification Error=====")


def console_print_monthly(finances: Finances):
    f = finances
    # Sort the month keys and print in month order
    sorted_month_keys = sorted(finances.monthly_finances.keys())
    for month_key in sorted_month_keys:
        month_obj = finances.monthly_finances[month_key]

        print("="*80)
        print(str(month_key))
        print(
            f"Income: {USD(month_obj.income.income_sum)}")
        print(
            f"\tWork income: {USD(month_obj.income.workincomesum)}")
        print_top(month_obj.income.nonworkincome, f)
        print(
            f"\Returns income: {USD(month_obj.income.returnsincomesum)}")
        print(
            f"Expenses: {USD(month_obj.expense.expensessum)}")
        print(f"Savings: {USD(month_obj.savings.amount_saved)}")
        print(f"Saving Percentage: {percent(month_obj.savings.saving_ratio)}")
        print(f"Top expenses:")
        print_top(month_obj.expense.expenses, f, 10)
        print(f"Top expense groups:")
        egc = month_obj.expense.expensegroupcoll
        for eg_i in egc.group_sums_sorted[:5]:
            print(
                f"\t{egc.group_keys[eg_i]}\t{USD(egc.group_sums[eg_i])}")
        print()


def console_print_summary(finances: Finances):
    f = finances

    # Print out 12-month report
    print()
    print("="*80)
    print(f"Since {finances.whole_finances.cutoff_date}:")
    print(f"Income: {USD(finances.whole_finances.income.income_sum)}")
    print(
        f"Work Income: {USD(finances.whole_finances.income.workincomesum)}")
    print(f"Biggest Non-Work Income:")
    print_top(finances.whole_finances.income.nonworkincome, f)
    print(
        f"Returns Income: {USD(finances.whole_finances.income.returnsincomesum)}")
    print(f"Expenses: {USD(finances.whole_finances.expense.expensessum)}")
    print(
        f"Gross Savings: {USD(finances.whole_finances.gross_savings.amount_saved)}")
    print(
        f"Gross Saving Percentage: {percent(finances.whole_finances.gross_savings.saving_ratio)}")
    print(
        f"Gross Avg Monthly Savings: {USD(finances.whole_finances.avg_monthly_savings.amount_saved)}")
    print(
        f"Gross Avg Monthly Savings Goals for {finances.whole_finances.period_in_months} months:")
    savings = finances.whole_finances.avg_monthly_savings
    for i in range(len(savings.savings_goals)):
        print(
            f"\tGoal: {percent(savings.savings_goals[i])}\tGoal Amount: {USD(savings.savings_goal_amts[i])}\tLeftover: {USD(savings.savings_goal_leftover[i])}")
    print(f"Investments: {USD(finances.whole_finances.investments_sum)}")
    # print_top(finances.whole_finances.investments, f)
    print(f"Biggest Expense Groups:")
    egc = finances.whole_finances.expense.expensegroupcoll
    for eg_i in egc.group_sums_sorted[:20]:
        print(
            f"\t{egc.group_keys[eg_i]}\t{percent(egc.group_percentages[eg_i])}\t{USD(egc.group_sums[eg_i])}")
    # print(f"Top Ignored Transactions:")
    # print_top(finances.ignored, f, 20)


def console_print_test(finances: Finances):
    data = finances.source

    data_m_ignored = filter(
        lambda t: not t.classification in ['Internal', 'Investments'], data)

    balance = sum(map(lambda t: t.amt, data_m_ignored))
    print(f"Balance: {balance}")
