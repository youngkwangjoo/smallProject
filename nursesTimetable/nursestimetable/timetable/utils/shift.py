import random
from datetime import timedelta

def assign_shifts(nurses, start_date, end_date, holidays, vacation_days, total_off_days, total_work_days):
    schedule = []
    nurse_status = {nurse: {
        'total_shifts': 0,
        'day_shifts': 0,
        'evening_shifts': 0,
        'night_shifts': 0,
        'last_shift': None
    } for nurse in nurses}
    
    total_days = (end_date - start_date).days + 1

    def random_assign_first_day(current_date, available_nurses, num_day_evening_nurses, num_night_nurses):
        daily_schedule = {'date': current_date, 'shifts': []}

        # Day shift assignment
        day_nurses = random.sample(available_nurses, num_day_evening_nurses)
        for nurse in day_nurses:
            nurse_status[nurse]['total_shifts'] += 1
            nurse_status[nurse]['day_shifts'] += 1
            nurse_status[nurse]['last_shift'] = 'day'
            daily_schedule['shifts'].append({'nurse': nurse, 'shift': 'day'})

        # Evening shift assignment
        available_nurses_for_evening = [n for n in available_nurses if n not in day_nurses]
        evening_nurses = random.sample(available_nurses_for_evening, num_day_evening_nurses)
        for nurse in evening_nurses:
            nurse_status[nurse]['total_shifts'] += 1
            nurse_status[nurse]['evening_shifts'] += 1
            nurse_status[nurse]['last_shift'] = 'evening'
            daily_schedule['shifts'].append({'nurse': nurse, 'shift': 'evening'})

        # Night shift assignment
        available_nurses_for_night = [n for n in available_nurses if n not in day_nurses and n not in evening_nurses]
        night_nurses = random.sample(available_nurses_for_night, num_night_nurses)
        for nurse in night_nurses:
            nurse_status[nurse]['total_shifts'] += 1
            nurse_status[nurse]['night_shifts'] += 1
            nurse_status[nurse]['last_shift'] = 'night'
            daily_schedule['shifts'].append({'nurse': nurse, 'shift': 'night'})

        return daily_schedule

    def assign_from_second_day(current_date, available_nurses, num_day_evening_nurses, num_night_nurses):
        daily_schedule = {'date': current_date, 'shifts': []}
        
        available_day_nurses = sorted(available_nurses, key=lambda n: nurse_status[n]['day_shifts'])
        day_nurses = available_day_nurses[:num_day_evening_nurses]
        for nurse in day_nurses:
            nurse_status[nurse]['total_shifts'] += 1
            nurse_status[nurse]['day_shifts'] += 1
            nurse_status[nurse]['last_shift'] = 'day'
            daily_schedule['shifts'].append({'nurse': nurse, 'shift': 'day'})

        available_evening_nurses = sorted([n for n in available_nurses if n not in day_nurses], key=lambda n: nurse_status[n]['evening_shifts'])
        evening_nurses = available_evening_nurses[:num_day_evening_nurses]
        for nurse in evening_nurses:
            nurse_status[nurse]['total_shifts'] += 1
            nurse_status[nurse]['evening_shifts'] += 1
            nurse_status[nurse]['last_shift'] = 'evening'
            daily_schedule['shifts'].append({'nurse': nurse, 'shift': 'evening'})

        available_night_nurses = sorted([n for n in available_nurses if n not in day_nurses and n not in evening_nurses], key=lambda n: nurse_status[n]['night_shifts'])
        night_nurses = available_night_nurses[:num_night_nurses]
        for nurse in night_nurses:
            nurse_status[nurse]['total_shifts'] += 1
            nurse_status[nurse]['night_shifts'] += 1
            nurse_status[nurse]['last_shift'] = 'night'
            daily_schedule['shifts'].append({'nurse': nurse, 'shift': 'night'})

        return daily_schedule

    for day_count in range(total_days):
        current_date = start_date + timedelta(days=day_count)
        available_nurses = [nurse for nurse in nurses if str(nurse.id) not in vacation_days or current_date.strftime('%Y-%m-%d') not in vacation_days[str(nurse.id)]]

        # 주말인지 평일인지 확인
        is_weekend = current_date.weekday() >= 5  # 5가 Saturday, 6이 Sunday
        num_day_evening_nurses = 2 if is_weekend else 3
        num_night_nurses = 2

        if day_count == 0:
            daily_schedule = random_assign_first_day(current_date, available_nurses, num_day_evening_nurses, num_night_nurses)
        else:
            daily_schedule = assign_from_second_day(current_date, available_nurses, num_day_evening_nurses, num_night_nurses)

        schedule.append(daily_schedule)

    return schedule
