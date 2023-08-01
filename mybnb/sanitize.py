import datetime
import re

def sin(sin: str) -> int:
    return int(re.sub(r'\D', '', sin))

sin_pattern = r'\d{3}-?\d{3}-?\d{3}'

def date(date_str: str) -> datetime.date:
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
