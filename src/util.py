from decimal import Decimal

# Returns float to two decimal places with commas


def USD(val):
    return f"{float(val):,.2f}"


# Interprets float as a decimal and converts to a percentage to two decimal places with commas
def percent(val):
    return f"{float(val*100):,.2f}%"


def parse_decimal(string: str):
    try:
        return Decimal(string.replace(",", ""))
    except Exception as err:
        raise ValueError(f"Decimal parsing error on <{string}>") from err
