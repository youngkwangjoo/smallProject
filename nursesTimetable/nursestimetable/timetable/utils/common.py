# utils/common.py
def get_weekends(start_weekday, total_days):
    weekdays_map = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6
    }

    start_weekday_num = weekdays_map[start_weekday]
    weekends = []

    for day in range(total_days):
        current_day = (start_weekday_num + day) % 7
        if current_day == 5 or current_day == 6:
            weekends.append(day + 1)
    return weekends
