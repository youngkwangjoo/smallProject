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

    def random_assign_first_day(current_date, available_nurses):
        daily_schedule = {'date': current_date, 'shifts': []}

        for shift_type in ['day', 'evening', 'night']:
            num_required = 2 if shift_type == 'night' else 3
            shift_nurses = random.sample(available_nurses, num_required)
            
            for nurse in shift_nurses:
                nurse_status[nurse]['total_shifts'] += 1
                nurse_status[nurse][f'{shift_type}_shifts'] += 1
                nurse_status[nurse]['last_shift'] = shift_type
                daily_schedule['shifts'].append({'nurse': nurse, 'shift': shift_type})

        return daily_schedule

    def assign_from_second_day(current_date, available_nurses):
        daily_schedule = {'date': current_date, 'shifts': []}
        
        available_day_nurses = sorted(available_nurses, key=lambda n: nurse_status[n]['day_shifts'])
        day_nurses = available_day_nurses[:3]
        for nurse in day_nurses:
            nurse_status[nurse]['total_shifts'] += 1
            nurse_status[nurse]['day_shifts'] += 1
            nurse_status[nurse]['last_shift'] = 'day'
            daily_schedule['shifts'].append({'nurse': nurse, 'shift': 'day'})

        available_evening_nurses = sorted([n for n in available_nurses if n not in day_nurses], key=lambda n: nurse_status[n]['evening_shifts'])
        evening_nurses = available_evening_nurses[:3]
        for nurse in evening_nurses:
            nurse_status[nurse]['total_shifts'] += 1
            nurse_status[nurse]['evening_shifts'] += 1
            nurse_status[nurse]['last_shift'] = 'evening'
            daily_schedule['shifts'].append({'nurse': nurse, 'shift': 'evening'})

        available_night_nurses = sorted([n for n in available_nurses if n not in day_nurses and n not in evening_nurses], key=lambda n: nurse_status[n]['night_shifts'])
        night_nurses = available_night_nurses[:2]
        for nurse in night_nurses:
            nurse_status[nurse]['total_shifts'] += 1
            nurse_status[nurse]['night_shifts'] += 1
            nurse_status[nurse]['last_shift'] = 'night'
            daily_schedule['shifts'].append({'nurse': nurse, 'shift': 'night'})

        return daily_schedule

    for day_count in range(total_days):
        current_date = start_date + timedelta(days=day_count)
        available_nurses = [nurse for nurse in nurses if str(nurse.id) not in vacation_days or current_date.strftime('%Y-%m-%d') not in vacation_days[str(nurse.id)]]

        if day_count == 0:
            daily_schedule = random_assign_first_day(current_date, available_nurses)
        else:
            daily_schedule = assign_from_second_day(current_date, available_nurses)

        schedule.append(daily_schedule)

    return schedule
