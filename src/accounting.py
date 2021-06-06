import datetime
import os

import s3datasource
import spreadsheet
import datainput
import classify


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
    group_keys = list(set(map(lambda t: t.classification,trans)))
    group_mapping = [[] for k in group_keys]
    for t_i, t in enumerate(trans):
        group_i = group_keys.index(t.classification)
        group_mapping[group_i].append(t_i)
    
    # Calculate expense group sums
    group_sums = [sum(map(lambda t_i: trans[t_i].amt,group_mapping[eg_i])) for eg_i,k in enumerate(group_keys)]

    # Sort expense groups by their totals
    group_sorted = sorted(range(len(group_keys)),key=lambda eg_i: group_sums[eg_i])
    return [group_keys,group_sums,group_sorted]


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
    cutoff = datetime.datetime(year-1,month,1).date()
    last_years_data = [t for t in data if t.date >= cutoff]

    # Load classification rules
    rules_contents = None
    with open('classification_rules.csv','r') as fin:
        rules_contents = fin.read()
    rules = classify.process_rules(rules_contents)

    # Classify data
    classify.classify(last_years_data, rules)

    ignored_class = ['Internal','Investments']
    work_income_class = ['Income']
    investment_class = ['Investments']

    # Filter out internal trans
    whole_data = last_years_data
    wdata = list(filter(lambda t: not t.classification in ignored_class,whole_data))

    # Breakdown into months

    ## Group trans by month
    months_dict = {}
    def months_key(date_obj):
        return datetime.datetime.strptime(f"{date_obj.year}-{date_obj.month}", "%Y-%m").date()
    for t in wdata:
        key = months_key(t.date)
        if not key in months_dict:
            months_dict[key] = []
        month_list = months_dict[key]
        month_list.append(t)

    ## Turn groups into Month objects and classify income vs expenses
    for month_key in months_dict.keys():
        income = [t for t in months_dict[month_key] if t.amt > 0]
        expenses = [t for t in months_dict[month_key] if t.amt < 0]
        months_dict[month_key] = Month(month_key,income,expenses)

    ## Print out month by month results

    ### prints the top five trans by absolute dollar amount
    def printTop5(trans):
        for t in sorted(trans,key=lambda t: abs(float(t.amt)), reverse=True)[:5]:
            print(f"\t{float(t.amt)}\t{t.classification}\t{t.desc}")

    ### Sort the month keys and print in month order
    sorted_month_keys = sorted(months_dict.keys())
    for month_key in sorted_month_keys:
        month_obj = months_dict[month_key]

        # identify work income separate from other income
        work_income = [t for t in month_obj.income if t.classification in work_income_class]
        non_work_income = [t for t in month_obj.income if not t in work_income]

        [expense_group_keys,expense_group_sums,expense_group_sorted] = group_sort_transactions(month_obj.expense)

        print(str(month_key))
        print(f"Income: {USD(sum(map(lambda t: float(t.amt),month_obj.income)))}")
        print(f"\tWork income: {USD(sum(map(lambda t: float(t.amt),work_income)))}")
        printTop5(non_work_income)
        print(f"Expenses: {USD(sum(map(lambda t: float(t.amt),month_obj.expense)))}")
        print(f"Top expenses:")
        printTop5(month_obj.expense)
        print(f"Top expense groups:")
        for eg_i in expense_group_sorted[:5]:
            print(f"\t{expense_group_keys[eg_i]}\t{USD(expense_group_sums[eg_i])}")
        print()

    # Print out 12-month report
    income = [t for t in wdata if t.amt > 0]
    expenses = [t for t in wdata if t.amt < 0]
    investments = list(filter(lambda t: t.classification in investment_class,whole_data))

    # Calculate expense groups
    [expense_group_keys,expense_group_sums,expense_group_sorted] = group_sort_transactions(expenses)

    print()
    print(f"Since {cutoff}:")
    print(f"Income: {USD(sum(map(lambda t: t.amt,income)))}")
    print(f"Expenses: {USD(sum(map(lambda t: t.amt,expenses)))}")
    print(f"Investments: {USD(sum(map(lambda t: abs(t.amt),investments)))}")
    print(f"Biggest Expense Groups:")
    for eg_i in expense_group_sorted[:20]:
        print(f"\t{expense_group_keys[eg_i]}\t{USD(expense_group_sums[eg_i])}")



    # Print out unclassified data if any
    classified_data = [t for t in last_years_data if t.classification != 'none']
    unclassified_data = [t for t in last_years_data if t.classification == 'none']

    if len(unclassified_data) > 0:
        for t in unclassified_data:
            print(str(t))

        print(f"classified {len(list(classified_data))}")
        print(f"unclassified {len(list(unclassified_data))}")
        print(f"total data {len(list(last_years_data))}")



class Month():
    def __init__(self, date, income, expense):
        self.date = date
        self.income = income
        self.expense = expense



if __name__ == "__main__":
    compile_data()
