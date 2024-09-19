import random
from datetime import timedelta

def assign_shifts(nurses, start_date, end_date, holidays, senior_junior_pairs, vacation_days, total_off_days, total_work_days):
    if not senior_junior_pairs:
        seniors = []
        juniors = []
    else:
        seniors, juniors = zip(*senior_junior_pairs)

    schedule = []
    current_date = start_date
    nurse_status = {nurse: {
        'last_shift': None, 
        'consecutive_nights': 0, 
        'consecutive_days': 0, 
        'off_days': 0, 
        'total_shifts': 0,
        'last_off_day': None
    } for nurse in nurses}

    total_weekends_and_holidays = sum(1 for d in (start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1))
                                      if d.weekday() >= 5 or d in holidays)

    max_off_days_per_nurse = total_weekends_and_holidays

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
        selected_nurses = eligible_nurses[:num_required]  # 가능한 간호사만 배정
        
        if len(selected_nurses) < num_required:
            # 간호사 부족 시에 None을 추가해서 표시
            missing_count = num_required - len(selected_nurses)
            selected_nurses.extend([None] * missing_count)  # 부족한 간호사 수만큼 None 추가
        
        return selected_nurses

    while current_date <= end_date:
        is_weekend = current_date.weekday() >= 5
        is_holiday = current_date in holidays
        
        daily_schedule = {'date': current_date, 'shifts': []}
        
        if is_holiday or is_weekend:
            num_nurses = {'day': 2, 'evening': 2, 'night': 2}
        else:
            num_nurses = {'day': 2, 'evening': 2, 'night': 2}
        
        available_nurses = [nurse for nurse in nurses if current_date not in vacation_days.get(nurse, [])]

        for shift_type in ['day', 'evening', 'night']:
            shift_nurses = select_nurses(available_nurses, num_nurses[shift_type], shift_type)
            
            # None이 있는 경우 간호사 부족을 표시
            for nurse in shift_nurses:
                if nurse is None:
                    daily_schedule['shifts'].append({'nurse': '간호사 부족', 'shift': shift_type})
                else:
                    daily_schedule['shifts'].append({'nurse': nurse, 'shift': shift_type})
                    # 근무 배정된 간호사의 상태 업데이트
                    status = nurse_status[nurse]
                    status['last_shift'] = shift_type
                    status['total_shifts'] += 1
                    
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

        # 간호사들이 근무에 배정되지 않은 경우 off 처리
        for nurse in nurses:
            status = nurse_status[nurse]
            if nurse not in [shift['nurse'] for shift in daily_schedule['shifts']] and status['off_days'] < max_off_days_per_nurse:
                status['off_days'] += 1
                status['consecutive_days'] = 0
                status['consecutive_nights'] = 0
                status['last_off_day'] = current_date

        schedule.append(daily_schedule)
        current_date += timedelta(days=1)

    for nurse in nurses:
        status = nurse_status[nurse]
        
        # 근무가 부족한 간호사에게 시프트 추가
        while status['total_shifts'] < total_work_days - 1:
            for day_schedule in schedule:
                if len(day_schedule['shifts']) < 3 and nurse not in day_schedule['shifts']:
                    day_schedule['shifts'].append({'nurse': nurse, 'shift': 'day'})
                    status['total_shifts'] += 1
                if status['total_shifts'] >= total_work_days - 1:
                    break

        # 근무가 많은 간호사에게 시프트 제거
        while status['total_shifts'] > total_work_days + 1:
            for day_schedule in schedule:
                if nurse in day_schedule['shifts']:
                    day_schedule['shifts'].remove({'nurse': nurse, 'shift': 'day'})
                    status['total_shifts'] -= 1
                if status['total_shifts'] <= total_work_days + 1:
                    break
    return schedule
