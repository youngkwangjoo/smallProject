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
            
            # 부사수는 반드시 사수와 함께 근무
            for nurse in selected_nurses:
                if nurse in juniors:
                    senior = next(senior for senior, junior in senior_junior_pairs if junior == nurse)
                    if senior in eligible_nurses:
                        selected_nurses.append(senior)
                        eligible_nurses.remove(senior)
                
                # 사수는 다른 사수와 근무 가능
                elif nurse in seniors:
                    other_senior = next((senior for senior in seniors if senior in eligible_nurses), None)
                    if other_senior:
                        selected_nurses.append(other_senior)
                        eligible_nurses.remove(other_senior)

        # 간호사가 부족한 상태라도 남은 간호사만 배정하여 진행
        return selected_nurses[:num_required]


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
            daily_schedule['shifts'].extend([{'nurse': nurse, 'shift': shift_type} for nurse in shift_nurses])
            
            for nurse in shift_nurses:
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
