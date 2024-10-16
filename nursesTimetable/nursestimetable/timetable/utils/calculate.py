# utils/calculate.py

def calculate_min_nurses(total_days, total_off_days, weekends, nurses):
    # 주어진 total_days에서 휴무일을 제외하고 실제 근무일 계산
    total_working_days = total_days - total_off_days

    # 평일과 주말에 필요한 간호사 수 정의
    weekday_nurses_needed = 8  # 평일: 아침 3명, 저녁 3명, 야간 2명 = 8명 필요
    weekend_nurses_needed = 6  # 주말: 아침 2명, 저녁 2명, 야간 2명 = 6명 필요

    # 실제 필요한 간호사 근무 횟수 계산 (근무일 기준)
    total_nurse_shifts_needed = (total_working_days - len(weekends)) * weekday_nurses_needed
    total_nurse_shifts_needed += len(weekends) * weekend_nurses_needed  # 주말 계산 추가

    # 각 간호사의 상태 초기화
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

    # 각 간호사가 특정 시프트에 배정될 수 있는지 확인하는 함수
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

    # 한 간호사가 주당 최대 근무 가능한 일수와 시프트 수
    max_work_days_per_nurse = 5
    total_max_shifts_per_nurse = max_work_days_per_nurse * 3  # 하루에 3개의 시프트

    # 필요한 최소 간호사 수를 계산
    min_nurses_needed = total_nurse_shifts_needed // total_max_shifts_per_nurse
    if total_nurse_shifts_needed % total_max_shifts_per_nurse != 0:
        min_nurses_needed += 1  # 나머지 시프트가 있을

    # 각 간호사의 근무 배정을 시뮬레이션하여 최소 인원 계산
    for nurse_id in nurse_status:
        assigned_shifts = 0
        for day in range(total_working_days):
            # 해당 날짜가 주말인지 확인
            is_weekend = day + 1 in weekends
            if is_weekend:
                day_shifts_needed = weekend_nurses_needed // 3  # 주말은 아침, 저녁, 야간 2명씩 배정
                evening_shifts_needed = day_shifts_needed
                night_shifts_needed = 2
            else:
                day_shifts_needed = weekday_nurses_needed // 3  # 평일은 아침, 저녁 3명씩, 야간 2명
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

            # 5일 연속 근무한 간호사에게 휴무 부여
            if nurse_status[nurse_id]['consecutive_days'] >= 5:
                nurse_status[nurse_id]['off_count'] += 1
                nurse_status[nurse_id]['consecutive_days'] = 0

    # 최소 필요한 간호사 수 반환
    return max(min_nurses_needed, 1)
