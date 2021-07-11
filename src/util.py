
# Returns float to two decimal places with commas
def USD(val):
    return f"{float(val):,.2f}"


# Interprets float as a decimal and converts to a percentage to two decimal places with commas
def percent(val):
    return f"{float(val*100):,.2f}%"
