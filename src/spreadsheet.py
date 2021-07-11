from typing import Sequence
from openpyxl import Workbook
from datetime import datetime
from operator import attrgetter, itemgetter

from openpyxl.worksheet.worksheet import Worksheet
from compile import Finances

from datafilter import filter_data
from datainput import Transaction
from util import USD


def build_spreadsheet(c, data, outputpath):
    wb = Workbook()
    summaryws = wb.active
    incomews = wb.create_sheet()
    expensews = wb.create_sheet()

    filtered_data = filter_data(c, data)
    leftover_data = set(data) - set(filtered_data)
    data = filtered_data

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
    summaryws.append(["All Time Income", f"={income_sum_addr}"])
    summaryws.append(["All Time Expense", f"={expense_sum_addr}"])
    summaryws.append(["All Time Net", f"=B1+B2"])
    summaryws.append(["All Time Savings Rate", f"=100*B3/B1"])

    months_dict = {}

    def months_key(date_obj):
        return datetime.strptime(f"{date_obj.year}-{date_obj.month}", "%Y-%m").date()
    for d in data:
        key = months_key(d.date)
        month_obj = None
        if key in months_dict:
            month_obj = months_dict[key]
        else:
            month_obj = Month(key, [], [])
            months_dict[key] = month_obj
        if d.amt > 0:
            month_obj.income.append(d)
        else:
            month_obj.expense.append(d)

    summaryws.append([])
    summaryws.append(["Date", "Income", "Expense", "Net"])
    months_list = [(k, months_dict[k]) for k in months_dict]
    for month_t in sorted(months_list, key=itemgetter(0), reverse=True):
        date = month_t[0]
        month = month_t[1]
        income = sum(map(lambda x: x.amt, month.income))
        expense = sum(map(lambda x: x.amt, month.expense))
        row = summaryws.max_row + 1
        summaryws.append([date, income, expense, f"=B{row}+C{row}"])

        ws = wb.create_sheet()
        ws.title = datetime.strftime(date, "%Y-%m")
        ws.append(["Income"])
        ws.append(["Date", "Description", "Amount"])
        for item in sorted(month.income, key=attrgetter("amt"), reverse=True):
            ws.append([item.date, item.desc, item.amt])
        ws.append(["", "", f"=SUM(C3:C{ws.max_row})"])
        income_sum_addr = f"C{ws.max_row}"

        ws.append([])
        ws.append(["Expenses"])
        ws.append(["Date", "Description", "Amount", "Income %"])
        for item in sorted(month.expense, key=attrgetter("amt")):
            ws.append([item.date, item.desc, item.amt,
                      f"=-100*C{ws.max_row + 1}/{income_sum_addr}"])

    leftoverws = wb.create_sheet()
    leftoverws.title = "Leftover Data"

    leftoverws.append(["Date", "Description", "Amount"])
    for item in sorted(leftover_data, key=attrgetter("date"), reverse=True):
        leftoverws.append([item.date, item.desc, item.amt])

    wb.save(outputpath)


def tab_append_data(finances: Finances, tab: Worksheet, data: Sequence[int]):
    trans = map(lambda i: finances.ix(i), data)
    tab_append_trans(tab, trans)


def tab_append_trans(tab, data: Sequence[Transaction]):
    tab.append(["Date", "Amount", "Class", "Description", "Source"])
    for t in sorted(data, key=lambda t: abs(t.amt), reverse=True):
        tab.append([t.date, USD(t.amt), t.classification, t.desc, t.source])


def create_spreadsheet(finances: Finances, output_filepath: str):
    wb = Workbook()
    summaryws = wb.active

    # Create year summary tab
    year = finances.whole_finances
    summaryws.title = "Year Summary"
    summaryws.append(["Year Income", f"{year.income.income_sum}"])
    summaryws.append(["Year Work Income", f"{year.income.workincomesum}"])
    summaryws.append(
        ["Year Non-Work Income", f"{year.income.nonworkincomesum}"])
    summaryws.append(
        ["Year Returns Income", f"{year.income.returnsincomesum}"])
    summaryws.append(["Year Expenses", f"{year.expense.expensessum}"])
    summaryws.append(["Year Investments", f"{year.investments_sum}"])

    # Year Income tab
    tab = wb.create_sheet()
    tab.title = "Year Income"
    tab_append_data(finances, tab, year.income.income)

    # Year Work Income tab
    tab = wb.create_sheet()
    tab.title = "Year Work Income"
    tab_append_data(finances, tab, year.income.workincome)

    # Year Non-work Income tab
    tab = wb.create_sheet()
    tab.title = "Year Non-work Income"
    tab_append_data(finances, tab, year.income.nonworkincome)

    # Year Returns Income tab
    tab = wb.create_sheet()
    tab.title = "Year Returns Income"
    tab_append_data(finances, tab, year.income.returnsincome)

    # Year Expenses tab
    tab = wb.create_sheet()
    tab.title = "Year Expenses"
    tab_append_data(finances, tab, year.expense.expenses)

    # Year Investments tab
    tab = wb.create_sheet()
    tab.title = "Year Investments"
    tab_append_data(finances, tab, year.investments)

    # Ignored Transactions tab
    tab = wb.create_sheet()
    tab.title = "Ignored Transactions"
    tab_append_data(finances, tab, finances.ignored)

    # Source Data tab
    tab = wb.create_sheet()
    tab.title = "Source Data"
    tab_append_trans(tab, finances.source)

    wb.save(output_filepath)


class Month():
    def __init__(self, date, income, expense):
        self.date = date
        self.income = income
        self.expense = expense
