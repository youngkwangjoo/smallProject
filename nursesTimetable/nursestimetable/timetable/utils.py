import random
from datetime import timedelta

def assign_shifts(nurses, start_date, end_date):
    schedule = []
    current_date = start_date
    
    while current_date <= end_date:
        weekday = current_date.weekday()
        is_weekend = weekday >= 5  # 주말 여부 확인
        
        daily_schedule = {'date': current_date, 'shifts': []}
        
        # 근무할 간호사 수 설정
        num_day_nurses = 2 if is_weekend else 3
        num_evening_nurses = 2 if is_weekend else 3
        num_night_nurses = 2

        # nurses가 리스트 형태인지 확인
        nurses_list = list(nurses)  # 만약 nurses가 쿼리셋이라면 리스트로 변환

        # 근무할 간호사 무작위 선택
        day_nurses = random.sample(nurses_list, num_day_nurses)
        evening_nurses = random.sample(nurses_list, num_evening_nurses)
        night_nurses = random.sample(nurses_list, num_night_nurses)
        
        daily_schedule['shifts'].extend([
            {'nurse': nurse, 'shift': 'day'} for nurse in day_nurses
        ])
        daily_schedule['shifts'].extend([
            {'nurse': nurse, 'shift': 'evening'} for nurse in evening_nurses
        ])
        daily_schedule['shifts'].extend([
            {'nurse': nurse, 'shift': 'night'} for nurse in night_nurses
        ])
        
        schedule.append(daily_schedule)
        current_date += timedelta(days=1)
    
    return schedule
