# utils.py

import datetime
import pytz

def get_current_time():
    return datetime.datetime.now(pytz.timezone("Africa/Nairobi")).strftime("%Y-%m-%d %H:%M:%S")

def format_currency(value):
    try:
        return f"${float(value):,.2f}"
    except:
        return "$0.00"

def percentage(part, whole):
    try:
        return round((float(part) / float(whole)) * 100, 2)
    except ZeroDivisionError:
        return 0.0
