from typing import Sequence
# import datetime
import os

import s3datasource
import spreadsheet
import datainput
import classify
import compile


# ignored_class = ['Internal', 'Investments']
# work_income_class = ['Income']
# investment_class = ['Investments']


def compile_data_into_spreadsheet():
    c = s3datasource.get_context()
    LOCAL_DATA_DIR = c.get_var("LOCAL_DATA_DIR")

    datasource = datainput.get_local_data_source(LOCAL_DATA_DIR)
    data = datainput.parse_data_source(datasource)

    run_id = c.get_run_id()
    outputpath = os.path.join(LOCAL_DATA_DIR, f"aaa-output-{run_id}.xlsx")

    spreadsheet.build_spreadsheet(c, data, outputpath)
    return outputpath


def run():
    c = s3datasource.get_context()
    LOCAL_DATA_DIR = c.get_var("LOCAL_DATA_DIR")

    # Load classification rules
    rules_contents = None
    with open('classification_rules.csv', 'r') as fin:
        rules_contents = fin.read()
    rules = classify.process_rules(rules_contents)

    # Load data
    datasource = datainput.get_local_data_source(LOCAL_DATA_DIR)
    data_all_time = datainput.parse_data_source(datasource)

    finances = compile.compile_data(data_all_time, rules)

    # # Create a year cutoff
    # now = datetime.datetime.now()
    # year = now.year
    # month = now.month
    # cutoff = datetime.datetime(year-1, month, 1).date()
    # main_data = [t for t in data_all_time if t.date >= cutoff]
    # def ix(i): return main_data[i]

    # # Classify data
    # classify.classify(main_data, rules)

    # # Filter out internal trans
    # wdata = list(
    #     filter(lambda i: not ix(i).classification in ignored_class, range(len(main_data))))

    # # Breakdown into months

    # # Group trans by month
    # from typing import Dict
    # months_dict: Dict[datetime.date, Month] = {}

    # def months_key(date_obj):
    #     return datetime.datetime.strptime(f"{date_obj.year}-{date_obj.month}", "%Y-%m").date()
    # for i in wdata:
    #     key = months_key(ix(i).date)
    #     if not key in months_dict:
    #         months_dict[key] = []
    #     month_list = months_dict[key]
    #     month_list.append(i)

    # # Turn groups into Month objects and classify income vs expenses
    # for month_key in months_dict.keys():
    #     i, e = analyze_financial_data(months_dict[month_key], ix)
    #     months_dict[month_key] = Month(month_key, i, e)

    # total_i, total_e = analyze_financial_data(wdata, ix)
    # investments = list(
    #     filter(lambda i: ix(i).classification in investment_class, range(len(main_data))))
    # investments_sum = sum(map(lambda i: ix(i).amt, investments))
    # year_finances = Year(cutoff, total_i, total_e,
    #                      investments, investments_sum)
    # classified = [
    #     i for i in range(len(main_data)) if ix(i).classification != 'none']
    # unclassified = [
    #     i for i in range(len(main_data)) if ix(i).classification == 'none']

    # finances = Finances(main_data, year_finances,
    #                     months_dict, classified, unclassified)

    # Print out month by month results

    f = finances

    def USD(val):
        return "{:.2f}".format(float(val))

    # prints the top five trans by absolute dollar amount

    def printTop5(data_is: Sequence[int]):
        for i in sorted(data_is, key=lambda i: abs(float(f.ix(i).amt)), reverse=True)[:5]:
            t = f.ix(i)
            print(f"\t{float(t.amt)}\t{t.classification}\t{t.desc}")

    # Sort the month keys and print in month order
    sorted_month_keys = sorted(finances.month_finances.keys())
    for month_key in sorted_month_keys:
        month_obj = finances.month_finances[month_key]

        print(str(month_key))
        print(
            f"Income: {USD(month_obj.income.income_sum)}")
        print(
            f"\tWork income: {USD(month_obj.income.workincomesum)}")
        printTop5(month_obj.income.nonworkincome)
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


if __name__ == "__main__":
    run()
