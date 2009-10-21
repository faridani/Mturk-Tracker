import datetime
def today():
    return datetime.date.today()

def tommorow():
    return today() + datetime.timedelta(days=1)

def yesterday():
    return today() - datetime.timedelta(days=1)
