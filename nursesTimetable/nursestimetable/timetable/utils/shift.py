import random
from datetime import timedelta

def assign_shifts(nurses, start_date, end_date, holidays, vacation_days, total_off_days, total_work_days):
    schedule = []

    # nurse 리스트는 id와 is_senior 속성을 가진다고 가정
    nurse_status = {nurse['id']: {
        'total_shifts': 0,
        'day_shifts': 0,
        'evening_shifts': 0,
        'night_shifts': 0,
        'consecutive_days': 0,  # 연속 근무 일수
        'last_shift': None,
        'off_count': 0,  # night 근무 후 두 타임 off 처리
        'is_senior': nurse['is_senior']
    } for nurse in nurses}
    # 한달
    total_days = (end_date - start_date).days + 1

    # 사수와 부사수 배정 규칙을 반영한 근무 가능 여부 판단 함수
    def is_available_for_shift(nurse_id, shift_type):
        nurse = nurse_status[nurse_id]
        # off 상태에 있으면 근무 불가
        if nurse['off_count'] > 0:
            return False
        # 연속 근무 5일 제한 후 off
        if nurse['consecutive_days'] >= 5:
            return False
        # evening 근무 후 day 근무 불가
        if shift_type == 'day' and nurse['last_shift'] == 'evening':
            return False
        # night 근무 후 evening 불가
        if shift_type == 'evening' and nurse['last_shift'] == 'night':
            return False
        return True

    # 사수와 부사수를 고려한 근무 배정 로직
    def assign_shift_for_shift_type(current_date, available_nurses, shift_type, num_nurses_needed):
        daily_schedule = []
        
        # 근무 가능한 사수들만 필터링
        senior_nurses = [nurse for nurse in available_nurses if nurse_status[nurse['id']]['is_senior'] and is_available_for_shift(nurse['id'], shift_type)]
        other_nurses = [nurse for nurse in available_nurses if not nurse_status[nurse['id']]['is_senior'] and is_available_for_shift(nurse['id'], shift_type)]

        # 근무 가능한 사수 중 1명을 배정
        if len(senior_nurses) > 0:
            assigned_seniors = random.sample(senior_nurses, 1)  # 근무 가능한 사수 중에서 무작위로 1명 배정
        else:
            assigned_seniors = []  # 사수가 없으면 빈 리스트로 처리

        # 나머지 인원은 사수/부사수 구분 없이 배정
        remaining_nurses_needed = num_nurses_needed - len(assigned_seniors)
        assigned_others = random.sample(other_nurses, min(remaining_nurses_needed, len(other_nurses)))

        assigned_nurses = assigned_seniors + assigned_others

        for nurse in assigned_nurses:
            nurse_status[nurse['id']]['total_shifts'] += 1
            nurse_status[nurse['id']][f'{shift_type}_shifts'] += 1
            nurse_status[nurse['id']]['last_shift'] = shift_type
            nurse_status[nurse['id']]['consecutive_days'] += 1
            daily_schedule.append({'nurse': nurse['id'], 'shift': shift_type})

        return daily_schedule


    for day_count in range(total_days):
        current_date = start_date + timedelta(days=day_count)
        available_nurses = [nurse for nurse in nurses if str(nurse['id']) not in vacation_days or current_date.strftime('%Y-%m-%d') not in vacation_days[str(nurse['id'])]]

        # 주말인지 평일인지 확인
        is_weekend = current_date.weekday() >= 5  # 5가 Saturday, 6이 Sunday
        num_day_evening_nurses = 2 if is_weekend else 3
        num_night_nurses = 2

        # off 처리
        for nurse_id in nurse_status:
            if nurse_status[nurse_id]['off_count'] > 0:
                nurse_status[nurse_id]['off_count'] -= 1  # off 상태 업데이트

        # 근무 배정 (사수-부사수 규칙 포함)
        daily_schedule = []
        daily_schedule.extend(assign_shift_for_shift_type(current_date, available_nurses, 'day', num_day_evening_nurses))
        daily_schedule.extend(assign_shift_for_shift_type(current_date, available_nurses, 'evening', num_day_evening_nurses))
        daily_schedule.extend(assign_shift_for_shift_type(current_date, available_nurses, 'night', num_night_nurses))

        schedule.append({'date': current_date, 'shifts': daily_schedule})

    return schedule
