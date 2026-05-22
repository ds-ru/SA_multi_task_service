from datetime import date, timedelta

def get_prev_month_range():
    today = date.today()
    first_day_current_month = today.replace(day=1)
    end_prev_month = first_day_current_month - timedelta(days=1)
    start_prev_month = end_prev_month.replace(day=1)
    return start_prev_month, end_prev_month

start_prev_month, end_prev_month = get_prev_month_range()
