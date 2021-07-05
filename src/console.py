from typing import Sequence


def USD(val):
    return "{:.2f}".format(float(val))

# prints the top five trans by absolute dollar amount


def printTop5(data_is: Sequence[int], f):
    for i in sorted(data_is, key=lambda i: abs(float(f.ix(i).amt)), reverse=True)[:5]:
        t = f.ix(i)
        print(f"\t{float(t.amt)}\t{t.classification}\t{t.desc}")


def console_print(finances):

    f = finances

    # Sort the month keys and print in month order
    sorted_month_keys = sorted(finances.month_finances.keys())
    for month_key in sorted_month_keys:
        month_obj = finances.month_finances[month_key]

        print(str(month_key))
        print(
            f"Income: {USD(month_obj.income.income_sum)}")
        print(
            f"\tWork income: {USD(month_obj.income.workincomesum)}")
        printTop5(month_obj.income.nonworkincome, f)
        print(
            f"Expenses: {USD(month_obj.expense.expensessum)}")
        print(f"Top expenses:")
        printTop5(month_obj.expense.expenses, f)
        print(f"Top expense groups:")
        egc = month_obj.expense.expensegroupcoll
        for eg_i in egc.group_sums_sorted[:5]:
            print(
                f"\t{egc.group_keys[eg_i]}\t{USD(egc.group_sums[eg_i])}")
        print()

    # Print out 12-month report
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
    if len(finances.unclassified) > 0:
        for i in finances.unclassified:
            print(str(f.ix(i)))

        print(f"classified {len(finances.classified)}")
        print(f"unclassified {len(finances.unclassified)}")
        print(f"total data {len(finances.source)}")
