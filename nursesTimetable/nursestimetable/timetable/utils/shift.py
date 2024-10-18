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
        if nurse['total_shifts'] >= total_work_days:  # 총 근무 횟수가 초과되지 않도록 제한
            return False
        if shift_type == 'day' and nurse['last_shift'] == 'evening':
            return False
        if shift_type == 'evening' and nurse['last_shift'] == 'night':
            return False
        return True

    # 사수 먼저 배정 후 부사수 및 나머지 배정
    def assign_shift_for_shift_type(current_date, available_nurses, shift_type, num_nurses_needed, already_assigned):
        daily_schedule = []
        assigned_nurses = []

        # 1. 사수 중 근무 횟수가 적은 순으로 정렬
        senior_nurses = sorted([nurse for nurse in available_nurses if nurse_status[nurse['id']]['is_senior'] 
                                and nurse['id'] not in already_assigned  # 이미 배정된 간호사는 제외
                                and is_available_for_shift(nurse['id'], shift_type)],
                                key=lambda x: nurse_status[x['id']][f'{shift_type}_shifts'])  # 해당 시프트 근무 횟수 기준으로 정렬

        # 2. 사수 중 근무 횟수가 가장 적은 사수 1명 배정
        if senior_nurses:
            assigned_seniors = senior_nurses[:1]  # 근무가 가장 적은 사수 1명 선택
            assigned_nurses += assigned_seniors
            remaining_nurses_needed = num_nurses_needed - 1  # 사수 1명 배정했으므로 나머지 인원 필요

            # 사수 배정된 간호사를 제외한 나머지 간호사 필터링
            remaining_nurses = [nurse for nurse in available_nurses if nurse['id'] not in [s['id'] for s in assigned_seniors]]

            # 3. 나머지 간호사들 중 근무 횟수가 적은 순으로 정렬 (사수 제외)
            all_nurses_sorted = sorted([nurse for nurse in remaining_nurses if is_available_for_shift(nurse['id'], shift_type)],
                                       key=lambda x: nurse_status[x['id']]['total_shifts'])  # 총 근무 횟수 기준으로 정렬

            # 4. 나머지 근무 인원 배정 (근무가 적은 순으로 배정)
            assigned_others = all_nurses_sorted[:remaining_nurses_needed]
            assigned_nurses += assigned_others

        # 5. 배정된 간호사들 상태 업데이트
        for nurse in assigned_nurses:
            nurse_status[nurse['id']]['total_shifts'] += 1
            nurse_status[nurse['id']][f'{shift_type}_shifts'] += 1  # 해당 시프트 근무 횟수 업데이트
            nurse_status[nurse['id']]['last_shift'] = shift_type
            nurse_status[nurse['id']]['consecutive_days'] += 1

            if nurse_status[nurse['id']]['consecutive_days'] >= 5:
                nurse_status[nurse['id']]['off_count'] = 1
                nurse_status[nurse['id']]['consecutive_days'] = 0

            daily_schedule.append({'nurse': nurse['id'], 'shift': shift_type})

        return daily_schedule


    # 총 일수 동안 매일 스케줄을 생성
    for day_count in range(total_days):
        current_date = day_count + 1
        is_weekend = current_date in weekends
        num_day_evening_nurses = 2 if is_weekend else 3
        num_night_nurses = 2

        available_nurses = [nurse for nurse in nurses if str(nurse['id']) not in vacation_days or current_date not in vacation_days[str(nurse['id'])]]

        # 하루에 이미 배정된 간호사 목록을 저장하는 집합 (중복 배정을 막기 위함)
        already_assigned = set()

        # 휴무 상태 업데이트
        for nurse_id in nurse_status:
            if nurse_status[nurse_id]['off_count'] > 0:
                nurse_status[nurse_id]['off_count'] -= 1

        # 시프트 배정 (근무 횟수가 적고, 사수와 부사수 균형 유지)
        daily_schedule = []
        daily_schedule.extend(assign_shift_for_shift_type(current_date, available_nurses, 'day', num_day_evening_nurses, already_assigned))
        daily_schedule.extend(assign_shift_for_shift_type(current_date, available_nurses, 'evening', num_day_evening_nurses, already_assigned))
        daily_schedule.extend(assign_shift_for_shift_type(current_date, available_nurses, 'night', num_night_nurses, already_assigned))

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
