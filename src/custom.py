from analyze import standard_compilation
from compile import Finances
from util import USD, percent
import tabulate


def do_custom(cutoff: int):
    finances: Finances = standard_compilation(cutoff)
    period_in_months = finances.whole_finances.period_in_months

    print(f"Past {cutoff} Months")

    table = []
    headers = ["Category", "Average Monthly Amount",
               f"% of Work Income", f"% of Expenses"]

    work_income = abs(finances.whole_finances.income.workincomesum)
    avg_monthly_work_income = work_income / period_in_months

    expenses = abs(finances.whole_finances.expense.expensessum)
    avg_monthly_expenses = expenses / period_in_months

    rent_utilities_classes = ["Housing", "Utilities"]
    rent_utilities = filter(
        lambda t: t.classification in rent_utilities_classes, finances.source)
    avg_monthly_rent_utilites = sum(
        map(lambda t: abs(t.amt), rent_utilities)) / period_in_months
    rent_utilities_work_income_percent = avg_monthly_rent_utilites / avg_monthly_work_income
    rent_utilities_expenses_percent = avg_monthly_rent_utilites / avg_monthly_expenses
    table.append(["Rent & Utilities", USD(avg_monthly_rent_utilites), percent(
        rent_utilities_work_income_percent), percent(rent_utilities_expenses_percent)])
    # print(f"Avg Monthly Rent & Utilities:\t{USD(avg_monthly_rent_utilites)}\t"
    #       + f"% of Work Income:\t{percent(rent_utilities_work_income_percent)}\t"
    #       + f"% of Expenses:\t{percent(rent_utilities_expenses_percent)}")

    transportation_classes = ["Transportation"]
    transportation = filter(
        lambda t: t.classification in transportation_classes, finances.source)
    avg_monthly_transportation = sum(
        map(lambda t: abs(t.amt), transportation)) / period_in_months
    transportation_work_income_percent = avg_monthly_transportation / avg_monthly_work_income
    transportation_expenses_percent = avg_monthly_transportation / avg_monthly_expenses
    table.append(["Transportation", USD(avg_monthly_transportation), percent(
        transportation_work_income_percent), percent(transportation_expenses_percent)])
    # print(f"Avg Monthly Transportation:\t{USD(avg_monthly_transportation)}\t"
    #       + f"% of Work Income:\t{percent(transportation_work_income_percent)}\t"
    #       + f"% of Expenses:\t{percent(transportation_expenses_percent)}")

    groceries_cat_classes = ["Pet Expenses", "Groceries"]
    groceries_cat = filter(
        lambda t: t.classification in groceries_cat_classes, finances.source)
    avg_monthly_groceries_cat = sum(
        map(lambda t: abs(t.amt), groceries_cat)) / period_in_months
    groceries_cat_work_income_percent = avg_monthly_groceries_cat / avg_monthly_work_income
    groceries_cat_expenses_percent = avg_monthly_groceries_cat / avg_monthly_expenses
    table.append(["Groceries & Cat Expenses", USD(avg_monthly_groceries_cat), percent(
        groceries_cat_work_income_percent), percent(groceries_cat_expenses_percent)])
    # print(f"Avg Monthly Groceries & Cat Expenses:\t{USD(avg_monthly_groceries_cat)}\t"
    #       + f"% of Work Income:\t{percent(groceries_cat_work_income_percent)}\t"
    #       + f"% of Expenses:\t{percent(groceries_cat_expenses_percent)}")

    print(tabulate.tabulate(table, headers=headers))
