from typing import Sequence
from openpyxl import Workbook

from openpyxl.worksheet.worksheet import Worksheet
from compile import Finances

from datafilter import filter_data
from datainput import Transaction
from util import USD


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
