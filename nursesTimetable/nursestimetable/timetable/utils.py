import random
from datetime import timedelta

def assign_shifts(nurses, start_date, end_date, holidays, senior_junior_pairs, vacation_days, total_off_days):
    # Check if senior_junior_pairs is empty and handle it
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

    def is_eligible_for_shift(nurse, shift_type, current_date):
        status = nurse_status[nurse]
        if current_date in vacation_days.get(nurse, []):
            return False
        if status['consecutive_days'] >= 5:
            return False
        if shift_type == 'night' and status['consecutive_nights'] >= 3:
            return False
        if status['last_shift'] == 'night' and (current_date - status['last_off_day']).days < 2:
            return False
        if shift_type == 'day' and status['last_shift'] == 'evening':
            return False
        if shift_type == 'night' and status['last_shift'] == 'evening':
            return False
        return True

    def select_nurses(available_nurses, num_required, shift_type):
        eligible_nurses = [nurse for nurse in available_nurses if is_eligible_for_shift(nurse, shift_type, current_date)]
        if len(eligible_nurses) < num_required:
            # 부족한 간호사 수를 반환하거나 로그에 기록
            print(f"Not enough nurses available for {shift_type} shift on {current_date}. Available: {len(eligible_nurses)}, Required: {num_required}")
            return eligible_nurses  # 부족한 상태로 반환

        selected_nurses = []
        for _ in range(num_required):
            if not eligible_nurses:
                break
            nurse = min(eligible_nurses, key=lambda n: nurse_status[n]['total_shifts'])
            selected_nurses.append(nurse)
            eligible_nurses.remove(nurse)
            
            # 사수-부사수 관계 확인
            if nurse in juniors:
                senior = next(senior for senior, junior in senior_junior_pairs if junior == nurse)
                if senior in eligible_nurses:
                    selected_nurses.append(senior)
                    eligible_nurses.remove(senior)
            elif nurse in seniors:
                junior = next((junior for senior, junior in senior_junior_pairs if senior == nurse), None)
                if junior in eligible_nurses:
                    selected_nurses.append(junior)
                    eligible_nurses.remove(junior)
        
        return selected_nurses[:num_required]


    while current_date <= end_date:
        is_weekend = current_date.weekday() >= 5
        is_holiday = current_date in holidays
        
        daily_schedule = {'date': current_date, 'shifts': []}
        
        if is_holiday or is_weekend:
            num_nurses = {'day': 2, 'evening': 2, 'night': 2}
        else:
            num_nurses = {'day': 3, 'evening': 3, 'night': 2}
        
        available_nurses = [nurse for nurse in nurses if current_date not in vacation_days.get(nurse, [])]
        
        for shift_type in ['day', 'evening', 'night']:
            shift_nurses = select_nurses(available_nurses, num_nurses[shift_type], shift_type)
            daily_schedule['shifts'].extend([{'nurse': nurse, 'shift': shift_type} for nurse in shift_nurses])
            
            for nurse in shift_nurses:
                status = nurse_status[nurse]
                status['last_shift'] = shift_type
                status['total_shifts'] += 1
                
                # 연속 근무 일수 업데이트
                if shift_type == 'night':
                    status['consecutive_nights'] += 1
                    # Night shift 뒤에 off 처리
                    status['off_days'] += 2  # 다음 두 타임을 off로 처리
                    status['last_off_day'] = current_date + timedelta(days=1)  # 첫 번째 off 날짜
                else:
                    status['consecutive_nights'] = 0  # night이 아니므로 리셋
                    if shift_type in ['day', 'evening']:
                        status['consecutive_days'] += 1

                # 연속 근무 일수 체크
                if status['consecutive_days'] > 5:
                    status['off_days'] += 1
                    status['last_off_day'] = current_date
                    status['consecutive_days'] = 0  # 리셋

        # Off days 관리
        for nurse in nurses:
            status = nurse_status[nurse]
            if nurse not in [shift['nurse'] for shift in daily_schedule['shifts']]:
                status['off_days'] += 1
                status['consecutive_days'] = 0
                status['consecutive_nights'] = 0
                status['last_off_day'] = current_date
            else:
                # 연속 근무 일수 체크
                if status['consecutive_days'] < 5:
                    status['consecutive_days'] += 1
                else:
                    # 5일 근무 후 하루 쉬도록 설정
                    status['off_days'] += 1
                    status['last_off_day'] = current_date
                    status['consecutive_days'] = 0  # 리셋

        schedule.append(daily_schedule)
        current_date += timedelta(days=1)

    return schedule
