from utils.common import get_weekends # shift.py에서 get_weekends 함수 가져오기

def calculate_min_nurses(total_days, total_off_days, total_work_days, start_weekday, nurses):
    # 주어진 total_days에서 휴무일을 제외하고 실제 근무일 계산
    total_working_days = total_days - total_off_days

    # 주말을 계산
    weekends = get_weekends(start_weekday, total_days)

    # 평일과 주말에 필요한 간호사 수 정의
    weekday_nurses_needed = 8  # 평일: 아침 3명, 저녁 3명, 야간 2명 = 8명 필요
    weekend_nurses_needed = 6  # 주말: 아침 2명, 저녁 2명, 야간 2명 = 6명 필요

    # 주말이 리스트로 올바르게 계산되었는지 확인
    if isinstance(weekends, list):
        total_nurse_shifts_needed = (total_working_days - len(weekends)) * weekday_nurses_needed
        total_nurse_shifts_needed += len(weekends) * weekend_nurses_needed
    else:
        return {'error': 'weekends is not a valid list'}

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
        min_nurses_needed += 1  # 나머지 시프트가 있을 경우 간호사 한 명 추가 필요

    return max(min_nurses_needed, 1)
