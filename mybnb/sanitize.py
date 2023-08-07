import datetime
import re

def sin(sin: str) -> int:
    return int(re.sub(r'\D', '', sin))

sin_pattern = r'\d{3}-?\d{3}-?\d{3}'

def card_num(card_num: str) -> int:
    return int(re.sub(r'\D', '', card_num))

card_num_pattern = r'\d{4}-?\d{4}-?\d{4}-?\d{4}'

def date(date_str: str) -> datetime.date:
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
