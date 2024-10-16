import random
from datetime import timedelta
from .calculate import calculate_min_nurses
from .common import get_weekends

# 간호사 스케줄을 배정하는 함수
def assign_shifts(nurses, total_days, holidays, vacation_days, total_off_days, total_work_days, start_weekday):
    schedule = []

    # 간호사 상태 초기화
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

    # 주말 계산
    weekends = get_weekends(start_weekday, total_days)

    # 간호사가 특정 시프트에 배정될 수 있는지 확인하는 함수
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

    # 시프트 배정 로직
    def assign_shift_for_shift_type(current_date, available_nurses, shift_type, num_nurses_needed):
        daily_schedule = []
        # 시니어 및 주니어 간호사 리스트 구분
        senior_nurses = [nurse for nurse in available_nurses if nurse_status[nurse['id']]['is_senior'] and is_available_for_shift(nurse['id'], shift_type)]
        other_nurses = [nurse for nurse in available_nurses if not nurse_status[nurse['id']]['is_senior'] and is_available_for_shift(nurse['id'], shift_type)]

        # 시니어 간호사 1명 배정
        assigned_seniors = random.sample(senior_nurses, 1) if len(senior_nurses) > 0 else []
        remaining_nurses_needed = num_nurses_needed - len(assigned_seniors)
        assigned_others = random.sample(other_nurses, min(remaining_nurses_needed, len(other_nurses)))
        assigned_nurses = assigned_seniors + assigned_others

        for nurse in assigned_nurses:
            nurse_status[nurse['id']]['total_shifts'] += 1
            nurse_status[nurse['id']][f'{shift_type}_shifts'] += 1
            nurse_status[nurse['id']]['last_shift'] = shift_type
            nurse_status[nurse['id']]['consecutive_days'] += 1

            # 연속 근무일수가 5일인 경우, off_count를 증가하고 연속 근무일수를 초기화
            if nurse_status[nurse['id']]['consecutive_days'] >= 5:
                nurse_status[nurse['id']]['off_count'] = 1
                nurse_status[nurse['id']]['consecutive_days'] = 0

            daily_schedule.append({'nurse': nurse['id'], 'shift': shift_type})

        return daily_schedule

    # 총 일수 동안 매일 스케줄을 생성
    for day_count in range(total_days):
        current_date = day_count + 1
        is_weekend = current_date in weekends  # 주말 여부 확인
        num_day_evening_nurses = 2 if is_weekend else 3
        num_night_nurses = 2

        # 휴가 중이 아닌 간호사 필터링
        available_nurses = [nurse for nurse in nurses if str(nurse['id']) not in vacation_days or current_date not in vacation_days[str(nurse['id'])]]

        # 휴무 상태 업데이트
        for nurse_id in nurse_status:
            if nurse_status[nurse_id]['off_count'] > 0:
                nurse_status[nurse_id]['off_count'] -= 1

        # 시프트 배정
        daily_schedule = []
        daily_schedule.extend(assign_shift_for_shift_type(current_date, available_nurses, 'day', num_day_evening_nurses))
        daily_schedule.extend(assign_shift_for_shift_type(current_date, available_nurses, 'evening', num_day_evening_nurses))
        daily_schedule.extend(assign_shift_for_shift_type(current_date, available_nurses, 'night', num_night_nurses))

        schedule.append({'date': current_date, 'shifts': daily_schedule})

    # 근무 횟수 로그 출력
    for nurse_id, status in nurse_status.items():
        print(f"Nurse {nurse_id} - 총 근무 횟수: {status['total_shifts']}, Day: {status['day_shifts']}, Evening: {status['evening_shifts']}, Night: {status['night_shifts']}")

    # 최소 간호사 수 계산
    try:
        min_nurses_needed = calculate_min_nurses(total_days, total_off_days, total_work_days, start_weekday, nurses)
        print(f"최소 필요한 간호사 수: {min_nurses_needed}명")
    except Exception as e:
        print(f"Error during scheduling: {str(e)}")

    return schedule
