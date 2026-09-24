from dateutil.parser import parse
from datetime import date

def diff_days(start_date: date, end_date: date) -> int:
    if not isinstance(start_date, date) or not isinstance(end_date, date):
        print("Both arguments must be valid dates")
        return False
    start_parse = parse(start_date.strftime('%Y-%m-%d'))
    end_parse = parse(end_date.strftime('%Y-%m-%d'))
    difference = end_parse - start_parse
    return difference.days



uccs_start_date = date(2026, 8, 24)
uccs_end_date = date(2026, 12, 18)
current_date = date.today()

total_days = diff_days(uccs_start_date, uccs_end_date)
print("There are ", total_days, " days in the 2026 Fall semester.")

remaining_days = diff_days(current_date, uccs_end_date)
print("There are only ", remaining_days, " days left!")


