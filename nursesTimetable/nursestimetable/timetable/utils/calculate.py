# utils/calculate.py

def calculate_min_nurses(total_days, weekends, nurses):
    total_weekdays = total_days - len(weekends)
    total_weekends = len(weekends)

    weekday_nurses_needed = 8
    weekend_nurses_needed = 6

    total_nurse_shifts_needed = (total_weekdays * weekday_nurses_needed) + (total_weekends * weekend_nurses_needed)

    nurse_status = {nurse['id']: {
        'total_shifts': 0,
        'day_shifts': 0,
        'evening_shifts': 0,
        'night_shifts': 0,
        'consecutive_days': 0,
        'last_shift': None,
        'off_count': 0,
        'is_senior': nurse['is_senior']
    } for nurse in nurses}

    def is_available_for_shift(nurse_id, shift_type):
        nurse = nurse_status[nurse_id]
        if nurse['off_count'] > 0:
            return False
        if nurse['consecutive_days'] >= 5:
            return False
        if shift_type == 'day' and nurse['last_shift'] == 'evening':
            return False
        if shift_type == 'evening' and nurse['last_shift'] == 'night':
            return False
        return True

    max_work_days_per_nurse = 5
    total_max_shifts_per_nurse = max_work_days_per_nurse * 3

    min_nurses_needed = total_nurse_shifts_needed // total_max_shifts_per_nurse

    for nurse_id in nurse_status:
        assigned_shifts = 0
        for day in range(total_days):
            is_weekend = day + 1 in weekends
            day_shifts_needed = 2 if is_weekend else 3
            evening_shifts_needed = day_shifts_needed
            night_shifts_needed = 2

            if assigned_shifts < total_max_shifts_per_nurse:
                for shift_type, num_nurses_needed in [('day', day_shifts_needed), ('evening', evening_shifts_needed), ('night', night_shifts_needed)]:
                    available_nurses = [nurse for nurse in nurses if is_available_for_shift(nurse['id'], shift_type)]
                    if len(available_nurses) >= num_nurses_needed:
                        assigned_shifts += 1
                        nurse_status[nurse_id]['total_shifts'] += 1
                        nurse_status[nurse_id]['consecutive_days'] += 1
                        nurse_status[nurse_id]['last_shift'] = shift_type

            if nurse_status[nurse_id]['consecutive_days'] >= 5:
                nurse_status[nurse_id]['off_count'] += 1
                nurse_status[nurse_id]['consecutive_days'] = 0

    return max(min_nurses_needed, 1)
