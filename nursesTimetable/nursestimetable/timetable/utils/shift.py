import random
from datetime import timedelta
from .calculate import calculate_min_nurses


# 주말을 계산하는 함수
# 시작 요일과 전체 일수를 받아 주말 날짜(토요일, 일요일)를 리스트로 반환
def get_weekends(start_weekday, total_days):
    # 요일을 숫자로 변환하기 위한 매핑
    weekdays_map = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6
    }

    # 시작 요일을 숫자로 변환
    start_weekday_num = weekdays_map[start_weekday]
    weekends = []
    
    # 전체 일수 동안 각 날짜의 요일을 계산하여 토요일(5) 또는 일요일(6)인 경우 리스트에 추가
    for day in range(total_days):
        current_day = (start_weekday_num + day) % 7
        if current_day == 5 or current_day == 6:  # 토요일 또는 일요일
            weekends.append(day + 1)
    return weekends


# 간호사 스케줄을 배정하는 함수
# 간호사 목록, 총 일수, 휴일, 휴가일, 총 휴무일, 총 근무일, 시작 요일을 입력받아 스케줄을 생성
def assign_shifts(nurses, total_days, holidays, vacation_days, total_off_days, total_work_days, start_weekday):
    schedule = []

    # 각 간호사 상태 초기화
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
        # 휴무 중이면 배정 불가
        if nurse['off_count'] > 0:
            return False
        # 5일 연속 근무한 경우 배정 불가
        if nurse['consecutive_days'] >= 5:
            return False
        # 저녁 근무 후 바로 다음 날 아침 근무 불가
        if shift_type == 'day' and nurse['last_shift'] == 'evening':
            return False
        # 야간 근무 후 바로 저녁 근무 불가
        if shift_type == 'evening' and nurse['last_shift'] == 'night':
            return False
        return True

    # 시프트 타입(아침, 저녁, 야간)에 대해 간호사 배정하는 함수
# 연속 근무일수 초기화 로직 추가
    def assign_shift_for_shift_type(current_date, available_nurses, shift_type, num_nurses_needed):
        daily_schedule = []
        # 시니어 간호사 리스트와 주니어 간호사 리스트를 구분하여 배정
        senior_nurses = [nurse for nurse in available_nurses if nurse_status[nurse['id']]['is_senior'] and is_available_for_shift(nurse['id'], shift_type)]
        other_nurses = [nurse for nurse in available_nurses if not nurse_status[nurse['id']]['is_senior'] and is_available_for_shift(nurse['id'], shift_type)]

        # 시니어 간호사 1명을 무작위로 배정
        if len(senior_nurses) > 0:
            assigned_seniors = random.sample(senior_nurses, 1)
        else:
            assigned_seniors = []

        # 나머지 간호사들 배정
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
                nurse_status[nurse['id']]['off_count'] = 1  # 휴무
                nurse_status[nurse['id']]['consecutive_days'] = 0  # 연속 근무일 초기화

            daily_schedule.append({'nurse': nurse['id'], 'shift': shift_type})

        return daily_schedule


    # 총 일수 동안 매일 스케줄을 생성
    for day_count in range(total_days):
        current_date = day_count + 1
        is_weekend = current_date in weekends  # 현재 날짜가 주말인지 확인
        num_day_evening_nurses = 2 if is_weekend else 3  # 주말: 2명, 평일: 3명 배정
        num_night_nurses = 2  # 야간에는 항상 2명 배정

        # 휴가 중이 아닌 간호사 필터링
        available_nurses = [nurse for nurse in nurses if str(nurse['id']) not in vacation_days or current_date not in vacation_days[str(nurse['id'])]]

        # 각 간호사의 휴무 상태 업데이트
        for nurse_id in nurse_status:
            if nurse_status[nurse_id]['off_count'] > 0:
                nurse_status[nurse_id]['off_count'] -= 1

        daily_schedule = []
        # 각 시프트(아침, 저녁, 야간)에 대해 간호사 배정
        daily_schedule.extend(assign_shift_for_shift_type(current_date, available_nurses, 'day', num_day_evening_nurses))
        daily_schedule.extend(assign_shift_for_shift_type(current_date, available_nurses, 'evening', num_day_evening_nurses))
        daily_schedule.extend(assign_shift_for_shift_type(current_date, available_nurses, 'night', num_night_nurses))

        # 스케줄에 현재 날짜의 배정된 근무 추가
        schedule.append({'date': current_date, 'shifts': daily_schedule})

    # 각 간호사의 근무 횟수 출력
    for nurse_id, status in nurse_status.items():
        print(f"Nurse {nurse_id} - 총 근무 횟수: {status['total_shifts']}, Day: {status['day_shifts']}, Evening: {status['evening_shifts']}, Night: {status['night_shifts']}")

    min_nurses_needed = calculate_min_nurses(total_days, weekends, nurses)
    print(f"최소 필요한 간호사 수: {min_nurses_needed}명")

    return schedule



