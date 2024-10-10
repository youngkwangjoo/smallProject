import random
from datetime import timedelta

# 주말을 계산하는 함수
def get_weekends(start_weekday, total_days):
    weekdays_map = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6
    }

    start_weekday_num = weekdays_map[start_weekday]
    weekends = []
    for day in range(total_days):
        current_day = (start_weekday_num + day) % 7
        if current_day == 5 or current_day == 6:  # 토요일(5) 또는 일요일(6)
            weekends.append(day + 1)
    return weekends


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

    def assign_shift_for_shift_type(current_date, available_nurses, shift_type, num_nurses_needed):
        daily_schedule = []
        senior_nurses = [nurse for nurse in available_nurses if nurse_status[nurse['id']]['is_senior'] and is_available_for_shift(nurse['id'], shift_type)]
        other_nurses = [nurse for nurse in available_nurses if not nurse_status[nurse['id']]['is_senior'] and is_available_for_shift(nurse['id'], shift_type)]

        if len(senior_nurses) > 0:
            assigned_seniors = random.sample(senior_nurses, 1)
        else:
            assigned_seniors = []

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
        current_date = day_count + 1
        is_weekend = current_date in weekends
        num_day_evening_nurses = 2 if is_weekend else 3
        num_night_nurses = 2

        available_nurses = [nurse for nurse in nurses if str(nurse['id']) not in vacation_days or current_date not in vacation_days[str(nurse['id'])]]

        for nurse_id in nurse_status:
            if nurse_status[nurse_id]['off_count'] > 0:
                nurse_status[nurse_id]['off_count'] -= 1

        daily_schedule = []
        daily_schedule.extend(assign_shift_for_shift_type(current_date, available_nurses, 'day', num_day_evening_nurses))
        daily_schedule.extend(assign_shift_for_shift_type(current_date, available_nurses, 'evening', num_day_evening_nurses))
        daily_schedule.extend(assign_shift_for_shift_type(current_date, available_nurses, 'night', num_night_nurses))

        schedule.append({'date': current_date, 'shifts': daily_schedule})

    # 최소 간호사 수 계산 및 로그 출력
    min_nurses_needed = calculate_min_nurses(total_days, weekends)
    print(f"최소 필요한 간호사 수: {min_nurses_needed}명")

    # 각 간호사의 근무 횟수 출력
    for nurse_id, status in nurse_status.items():
        print(f"Nurse {nurse_id} - 총 근무 횟수: {status['total_shifts']}, Day: {status['day_shifts']}, Evening: {status['evening_shifts']}, Night: {status['night_shifts']}")

    return schedule


# 최소 간호사 수 계산 함수
def calculate_min_nurses(total_days, weekends):
    total_weekdays = total_days - len(weekends)
    total_weekends = len(weekends)

    weekday_nurses_needed = 8  # 평일: day 3명, evening 3명, night 2명 = 8명
    weekend_nurses_needed = 6  # 주말: day 2명, evening 2명, night 2명 = 6명
    
    total_nurse_shifts_needed = (total_weekdays * weekday_nurses_needed) + (total_weekends * weekend_nurses_needed)

    max_work_days_per_nurse = 5 * (total_days // 7)  # 한 간호사가 주당 최대 5일 근무 가능
    min_nurses_needed = total_nurse_shifts_needed // max_work_days_per_nurse
    
    return max(min_nurses_needed, 1)


# 프론트엔드에서 들어오는 데이터 예시
data = {
  "nurses": [
    { "id": 1, "name": "Nurse 1", "is_senior": True, "vacation_days": []},
    { "id": 2, "name": "Nurse 2", "is_senior": True, "vacation_days":  []},
    { "id": 3, "name": "Nurse 3", "is_senior": True, "vacation_days": [] },
    { "id": 4, "name": "Nurse 4", "is_senior": True, "vacation_days": [] },
    { "id": 5, "name": "Nurse 5", "is_senior": True, "vacation_days": [] },
    { "id": 6, "name": "Nurse 6", "is_senior": True, "vacation_days": [] },
    { "id": 7, "name": "Nurse 7", "is_senior": True, "vacation_days": [] },
    { "id": 8, "name": "Nurse 8", "is_senior": False, "vacation_days": [] },
    { "id": 9, "name": "Nurse 9", "is_senior": False, "vacation_days": [] },
    { "id": 10, "name": "Nurse 10", "is_senior": False, "vacation_days": [] },
    { "id": 11, "name": "Nurse 11", "is_senior": False, "vacation_days": [] },
    { "id": 12, "name": "Nurse 12", "is_senior": False, "vacation_days": [] },
    { "id": 13, "name": "Nurse 13", "is_senior": False, "vacation_days": [] }
  ],
  "total_off_days": 10,
  "total_work_days": 21,
  "total_days": 31,
  "start_weekday": "Tuesday"
}

# 스케줄 생성
assign_shifts(
    data['nurses'], 
    data['total_days'], 
    [],  # holidays가 없는 것으로 가정
    {nurse['id']: nurse['vacation_days'] for nurse in data['nurses']}, 
    data['total_off_days'], 
    data['total_work_days'], 
    data['start_weekday']
)
