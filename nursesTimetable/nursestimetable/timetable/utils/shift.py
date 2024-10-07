import random
from datetime import timedelta

def assign_shifts(nurses, start_date, end_date, holidays, vacation_days, total_off_days, total_work_days):
    schedule = []
    nurse_status = {nurse: {
        'total_shifts': 0,
        'day_shifts': 0,
        'evening_shifts': 0,
        'night_shifts': 0,
        'consecutive_days': 0,  # 연속 근무 일수
        'last_shift': None,
        'off_count': 0  # night 근무 후 두 타임 off 처리
    } for nurse in nurses}
    
    total_days = (end_date - start_date).days + 1

    # 근무 가능 여부를 판단하는 함수
    def is_available_for_shift(nurse, shift_type):
        # off 상태에 있으면 근무 불가
        if nurse_status[nurse]['off_count'] > 0:
            return False
        # 연속 근무 5일 제한 후 off
        if nurse_status[nurse]['consecutive_days'] >= 5:
            return False
        # evening 근무 후 day 근무 불가
        if shift_type == 'day' and nurse_status[nurse]['last_shift'] == 'evening':
            return False
        # night 근무 후 evening 불가
        if shift_type == 'evening' and nurse_status[nurse]['last_shift'] == 'night':
            return False
        # evening 근무 후 day 근무 불가
        if shift_type == 'day' and nurse_status[nurse]['last_shift'] == 'evening':
            return False
        return True

    def random_assign_first_day(current_date, available_nurses, num_day_evening_nurses, num_night_nurses):
        daily_schedule = {'date': current_date, 'shifts': []}

        required_nurses = num_day_evening_nurses * 2 + num_night_nurses
        if len(available_nurses) < required_nurses:
            print(f"Warning: 간호사 수가 부족합니다. {current_date}에 필요한 간호사 수는 {required_nurses}명이나, 배정 가능한 간호사는 {len(available_nurses)}명입니다.")

        # Day shift assignment
        day_nurses = random.sample(available_nurses, num_day_evening_nurses)
        for nurse in day_nurses:
            nurse_status[nurse]['total_shifts'] += 1
            nurse_status[nurse]['day_shifts'] += 1
            nurse_status[nurse]['last_shift'] = 'day'
            nurse_status[nurse]['consecutive_days'] += 1
            daily_schedule['shifts'].append({'nurse': nurse, 'shift': 'day'})

        # Evening shift assignment
        available_nurses_for_evening = [n for n in available_nurses if n not in day_nurses]
        evening_nurses = random.sample(available_nurses_for_evening, num_day_evening_nurses)
        for nurse in evening_nurses:
            nurse_status[nurse]['total_shifts'] += 1
            nurse_status[nurse]['evening_shifts'] += 1
            nurse_status[nurse]['last_shift'] = 'evening'
            nurse_status[nurse]['consecutive_days'] += 1
            daily_schedule['shifts'].append({'nurse': nurse, 'shift': 'evening'})

        # Night shift assignment
        available_nurses_for_night = [n for n in available_nurses if n not in day_nurses and n not in evening_nurses]
        night_nurses = random.sample(available_nurses_for_night, num_night_nurses)
        for nurse in night_nurses:
            nurse_status[nurse]['total_shifts'] += 1
            nurse_status[nurse]['night_shifts'] += 1
            nurse_status[nurse]['last_shift'] = 'night'
            nurse_status[nurse]['consecutive_days'] += 1
            nurse_status[nurse]['off_count'] = 2  # night 근무 후 2번 off
            daily_schedule['shifts'].append({'nurse': nurse, 'shift': 'night'})

        return daily_schedule

    def assign_from_second_day(current_date, available_nurses, num_day_evening_nurses, num_night_nurses):
        daily_schedule = {'date': current_date, 'shifts': []}
        
        required_nurses = num_day_evening_nurses * 2 + num_night_nurses
        if len(available_nurses) < required_nurses:
            print(f"Warning: 간호사 수가 부족합니다. {current_date}에 필요한 간호사 수는 {required_nurses}명이나, 배정 가능한 간호사는 {len(available_nurses)}명입니다.")        
            
        # 연속 근무 일수를 체크하고 off 설정
        for nurse in available_nurses:
            if nurse_status[nurse]['consecutive_days'] >= 5:
                nurse_status[nurse]['consecutive_days'] = 0
                nurse_status[nurse]['off_count'] = 3  # 5일 연속 근무 후 3번 off

        # Day shift assignment
        available_day_nurses = [n for n in available_nurses if is_available_for_shift(n, 'day')]
        day_nurses = sorted(available_day_nurses, key=lambda n: nurse_status[n]['day_shifts'])[:num_day_evening_nurses]
        for nurse in day_nurses:
            nurse_status[nurse]['total_shifts'] += 1
            nurse_status[nurse]['day_shifts'] += 1
            nurse_status[nurse]['last_shift'] = 'day'
            nurse_status[nurse]['consecutive_days'] += 1
            daily_schedule['shifts'].append({'nurse': nurse, 'shift': 'day'})

        # Evening shift assignment
        available_evening_nurses = [n for n in available_nurses if n not in day_nurses and is_available_for_shift(n, 'evening')]
        evening_nurses = sorted(available_evening_nurses, key=lambda n: nurse_status[n]['evening_shifts'])[:num_day_evening_nurses]
        for nurse in evening_nurses:
            nurse_status[nurse]['total_shifts'] += 1
            nurse_status[nurse]['evening_shifts'] += 1
            nurse_status[nurse]['last_shift'] = 'evening'
            nurse_status[nurse]['consecutive_days'] += 1
            daily_schedule['shifts'].append({'nurse': nurse, 'shift': 'evening'})

        # Night shift assignment
        available_night_nurses = [n for n in available_nurses if n not in day_nurses and n not in evening_nurses and is_available_for_shift(n, 'night')]
        night_nurses = sorted(available_night_nurses, key=lambda n: nurse_status[n]['night_shifts'])[:num_night_nurses]
        for nurse in night_nurses:
            nurse_status[nurse]['total_shifts'] += 1
            nurse_status[nurse]['night_shifts'] += 1
            nurse_status[nurse]['last_shift'] = 'night'
            nurse_status[nurse]['consecutive_days'] += 1
            nurse_status[nurse]['off_count'] = 2  # night 근무 후 2번 off
            daily_schedule['shifts'].append({'nurse': nurse, 'shift': 'night'})

        return daily_schedule

    for day_count in range(total_days):
        current_date = start_date + timedelta(days=day_count)
        available_nurses = [nurse for nurse in nurses if str(nurse.id) not in vacation_days or current_date.strftime('%Y-%m-%d') not in vacation_days[str(nurse.id)]]

        # 주말인지 평일인지 확인
        is_weekend = current_date.weekday() >= 5  # 5가 Saturday, 6이 Sunday
        num_day_evening_nurses = 2 if is_weekend else 3
        num_night_nurses = 2

        # off 처리
        for nurse in nurses:
            if nurse_status[nurse]['off_count'] > 0:
                nurse_status[nurse]['off_count'] -= 1  # off 상태 업데이트

        if day_count == 0:
            daily_schedule = random_assign_first_day(current_date, available_nurses, num_day_evening_nurses, num_night_nurses)
        else:
            daily_schedule = assign_from_second_day(current_date, available_nurses, num_day_evening_nurses, num_night_nurses)

        schedule.append(daily_schedule)

    return schedule
