from openpyxl import Workbook
import re
import csv
from datetime import datetime
from operator import attrgetter, itemgetter

def read_debit(data, label):
    with open(f"csv/{label}.csv", "r", newline='') as fin:
        reader = csv.reader(fin)
        for i, row in enumerate(reader):
            if i < 8:
                continue

            date = row[0]
            description = row[1]
            amount = row[2]
            data.append(Transaction(
                date,
                description,
                amount,
                label,
                None,
            ))

def read_credit(data, label):
    with open(f"csv/{label}.csv", "r", newline='') as fin:
        reader = csv.reader(fin)
        for i, row in enumerate(reader):
            if i < 1:
                continue
            date = row[0]
            reference_number = row[1]
            description = row[2]
            amount = row[4]
            data.append(Transaction(
                date,
                description,
                amount,
                label,
                reference_number,
            ))

def clean_data(data):
    for d in data:
        amt = re.sub(r"\"", "", d.amt)
        d.amt = float(amt)

        d.date = datetime.strptime(d.date, "%m/%d/%Y").date()
    return data


def filter_data(data_old):
    data = []
    for d in data_old:
        if "Online Banking transfer" in d.desc:
            continue
        if "Online Banking payment" in d.desc:
            continue
        if "Online payment" in d.desc:
            continue
        data.append(d)
    return data

def main():
    data = []

    read_debit(data, "primary")
    read_debit(data, "secondary")
    read_credit(data, "November2018_2236")
    read_credit(data, "October2018_2236")
    read_credit(data, "currentTransaction_2236")

    wb = Workbook()
    summaryws = wb.active
    incomews = wb.create_sheet()
    expensews = wb.create_sheet()

    data = clean_data(data)
    data = filter_data(data)

    income_data = [d for d in data if d.amt > 0]
    expense_data = [d for d in data if d.amt < 0]

    incomews.title = "Income"
    incomews.append(["Date", "Description", "Amount"])
    for d in sorted(income_data, key=attrgetter("date"), reverse=True):
        incomews.append([d.date, d.desc, d.amt])
    incomews.append(["", "", f"=SUM(C2:C{incomews.max_row})"])
    income_sum_addr = f"{incomews.title}!C{incomews.max_row}"

    expensews.title = "Expenses"
    expensews.append(["Date", "Description", "Amount"])
    for d in sorted(expense_data, key=attrgetter("date"), reverse=True):
        expensews.append([d.date, d.desc, d.amt])
    expensews.append(["", "", f"=SUM(C2:C{expensews.max_row})"])
    expense_sum_addr = f"{expensews.title}!C{expensews.max_row}"

    summaryws.title = "Summary"
    summaryws.append(["Income", f"={income_sum_addr}"])
    summaryws.append(["Expense", f"={expense_sum_addr}"])
    summaryws.append(["Net", f"=B1+B2"])

    months_dict = {}
    def months_key(date_obj):
        return datetime.strptime(f"{date_obj.year}-{date_obj.month}", "%Y-%m").date()
    for d in data:
        key = months_key(d.date)
        month_obj = None
        if key in months_dict:
            month_obj = months_dict[key]
        else:
            month_obj = Month(key, [],[])
            months_dict[key] = month_obj
        if d.amt > 0:
            month_obj.income.append(d)
        else:
            month_obj.expense.append(d)

    summaryws.append([])
    summaryws.append(["Date", "Income", "Expense", "Net"])
    months_list = [(k, months_dict[k]) for k in months_dict]
    months_list = sorted(months_list, key=itemgetter(0), reverse=True)
    for month_t in months_list:
        date = month_t[0]
        month = month_t[1]
        income = sum(map(lambda x: x.amt, month.income))
        expense = sum(map(lambda x: x.amt, month.expense))
        row = summaryws.max_row + 1
        summaryws.append([date, income, expense, f"=B{row}+C{row}"])
    
    wb.save("output.xlsx")



class Transaction():
    def __init__(self, date, desc, amt, label, ref_num):
        self.date = date
        self.desc = desc
        self.amt = amt
        self.label = label
        self.ref_num = ref_num
    def __repl__(self):
        return f"{{ {self.date}, {self.desc}, {self.amt}, {self.label}, {self.ref_num},  }}"
    def __str__(self):
        return self.__repl__()

class Month():
    def __init__(self, date, income, expense):
        self.date = date
        self.income = income
        self.expense = expense


main()

