from datetime import timedelta
from .balance import balance_nurse_shifts, balance_shift_types
import random

def assign_shifts(nurses, start_date, end_date, holidays, vacation_days, total_off_days, total_work_days):
    # 스케줄 리스트를 초기화
    schedule = []

    # 간호사들의 상태를 저장할 딕셔너리
    nurse_status = {nurse: {
        'last_shift': None, 
        'consecutive_nights': 0, 
        'consecutive_days': 0, 
        'off_days': 0, 
        'total_shifts': 0,
        'day_shifts': 0,       # day 근무 카운트
        'evening_shifts': 0,   # evening 근무 카운트
        'night_shifts': 0,     # night 근무 카운트
        'last_off_day': None
    } for nurse in nurses}

    total_days = (end_date - start_date).days + 1  # 총 날짜 계산

    def is_eligible_for_shift(nurse, shift_type, current_date):
        status = nurse_status[nurse]

        # 이미 연속 5일 근무했다면 1일 off 후 근무 가능
        if status['consecutive_days'] >= 5:
            if (current_date - status['last_off_day']).days < 1:
                return False
            else:
                status['consecutive_days'] = 0  # 하루 쉰 후 다시 근무 가능하도록 초기화

        # 연속 night 근무 및 기타 규칙 적용
        if shift_type == 'night' and status['consecutive_nights'] >= 3:
            return False

        # 야간 근무 후 2타임(day, evening)은 근무 불가 (다시 night 근무는 가능)
        if status['last_shift'] == 'night':
            if shift_type in ['day', 'evening']:
                return False  # day와 evening은 불가
            if (current_date - status['last_off_day']).days == 0:  # 같은 날 night 근무 가능
                return True

        # 이브닝 근무 후 다음 날 day 근무 불가
        if shift_type == 'day' and status['last_shift'] == 'evening':
            return False

        # 이브닝 근무 후 night 근무 불가
        if shift_type == 'night' and status['last_shift'] == 'evening':
            return False

        if status['total_shifts'] >= total_work_days + 1:  # 근무일 수 초과 방지
            return False

        return True

    def select_nurses(available_nurses, num_required, shift_type):
        eligible_nurses = [nurse for nurse in available_nurses if is_eligible_for_shift(nurse, shift_type, current_date)]
        
        # 가능한 간호사만 배정하고, 부족하더라도 오류 없이 진행
        if len(eligible_nurses) < num_required:
            print(f"Not enough nurses available for {shift_type} shift on {current_date}. Available: {len(eligible_nurses)}, Required: {num_required}")
            selected_nurses = eligible_nurses  # 가능한 간호사만 선택
        else:
            selected_nurses = []
            for _ in range(num_required):
                if not eligible_nurses:
                    break
                nurse = min(eligible_nurses, key=lambda n: nurse_status[n]['total_shifts'])
                selected_nurses.append(nurse)
                eligible_nurses.remove(nurse)

        return selected_nurses[:num_required]

    # 날짜 루프를 for 문으로 변경
    for day_count in range(total_days):
        current_date = start_date + timedelta(days=day_count)  # 현재 날짜 계산
        is_weekend = current_date.weekday() >= 5
        is_holiday = current_date in holidays
        
        daily_schedule = {'date': current_date, 'shifts': []}
        
        # 주말 및 공휴일에 따른 간호사 수
        if is_holiday or is_weekend:
            num_nurses = {'day': 2, 'evening': 2, 'night': 2}
        else:
            num_nurses = {'day': 3, 'evening': 3, 'night': 2}
        
        # 근무 가능한 간호사 목록 생성
        available_nurses = [nurse for nurse in nurses if current_date not in vacation_days.get(nurse, [])]

        # 각 시프트에 대한 간호사 배정
        for shift_type in ['day', 'evening', 'night']:
            shift_nurses = select_nurses(available_nurses, num_nurses[shift_type], shift_type)
            daily_schedule['shifts'].extend([{'nurse': nurse, 'shift': shift_type} for nurse in shift_nurses])
            
            for nurse in shift_nurses:
                if nurse:  # 간호사가 None이 아닌 경우에만 상태 업데이트
                    status = nurse_status[nurse]
                    status['last_shift'] = shift_type
                    status['total_shifts'] += 1

                    # 근무 종류별 카운트 업데이트
                    if shift_type == 'day':
                        status['day_shifts'] += 1
                    elif shift_type == 'evening':
                        status['evening_shifts'] += 1
                    elif shift_type == 'night':
                        status['night_shifts'] += 1
                    
                    if shift_type == 'night':
                        status['consecutive_nights'] += 1
                        status['last_off_day'] = current_date  # night 근무 후, 같은 날에 다시 night 근무 가능하게 설정
                    else:
                        status['consecutive_nights'] = 0
                        if shift_type in ['day', 'evening']:
                            status['consecutive_days'] += 1

                    if status['consecutive_days'] >= 5:
                        status['last_off_day'] = current_date
                        status['consecutive_days'] = 0

        # 근무하지 않은 간호사 처리
        for nurse in nurses:
            status = nurse_status[nurse]
            if nurse not in [shift['nurse'] for shift in daily_schedule['shifts']] and status['off_days'] < total_off_days:
                status['off_days'] += 1
                status['consecutive_days'] = 0
                status['consecutive_nights'] = 0
                status['last_off_day'] = current_date

        schedule.append(daily_schedule)

    # 근무 횟수 균등화
    balance_nurse_shifts(nurse_status, schedule, total_work_days)

    # 근무 종류별 균등화
    balance_shift_types(nurse_status, schedule)
    
    # 결과 출력
    print("\n--- Nurse Work Counts ---")
    for nurse, status in nurse_status.items():
        print(f"{nurse}: 총 근무 횟수 = {status['total_shifts']} (Day: {status['day_shifts']}, Evening: {status['evening_shifts']}, Night: {status['night_shifts']})")

    return schedule
