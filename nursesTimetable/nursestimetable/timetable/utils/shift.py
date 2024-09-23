import random
from datetime import timedelta

def assign_shifts(nurses, start_date, end_date, holidays, vacation_days, total_off_days, total_work_days):
    schedule = []
    nurse_status = {nurse: {
        'total_shifts': 0,
        'day_shifts': 0,
        'evening_shifts': 0,
        'night_shifts': 0,
        'last_shift': None
    } for nurse in nurses}
    
    total_days = (end_date - start_date).days + 1

    # 간호사를 상위 4명, 중간 그룹, 하위 4명으로 나눔
    sorted_nurses = sorted(nurses, key=lambda n: n.id)  # id 또는 다른 기준으로 정렬
    top_4 = sorted_nurses[:4]
    bottom_4 = sorted_nurses[-4:]
    middle_group = sorted_nurses[4:-4]

    # 중간 그룹에 1~2회 더 나이트 근무 배정하도록 설정
    middle_group_night_limit = 2  # 중간 그룹에 1~2회 더 배정하려면 여기서 설정

    # 첫날 랜덤 배정
    def random_assign_first_day(current_date, available_nurses):
        daily_schedule = {'date': current_date, 'shifts': []}

        # 사수와 부사수 랜덤 페어로 배정
        for shift_type in ['day', 'evening', 'night']:
            num_required = 2 if shift_type == 'night' else 3  # 필요한 간호사 수
            shift_nurses = random.sample(available_nurses, num_required)
            
            for nurse in shift_nurses:
                nurse_status[nurse]['total_shifts'] += 1
                nurse_status[nurse][f'{shift_type}_shifts'] += 1
                nurse_status[nurse]['last_shift'] = shift_type
                daily_schedule['shifts'].append({'nurse': nurse, 'shift': shift_type})

        return daily_schedule

    # 2일차부터 근무 횟수가 적은 간호사 우선 배정
    # 2일차부터 나이트 근무 우선 배정
    # 2일차부터 나이트 근무 우선 배정
    def assign_from_second_day(current_date, available_nurses):
        daily_schedule = {'date': current_date, 'shifts': []}
        
        # Day 근무자 배정 (근무 횟수가 적은 순으로)
        available_day_nurses = sorted(available_nurses, key=lambda n: nurse_status[n]['day_shifts'])
        day_nurses = available_day_nurses[:3]
        for nurse in day_nurses:
            nurse_status[nurse]['total_shifts'] += 1
            nurse_status[nurse]['day_shifts'] += 1
            nurse_status[nurse]['last_shift'] = 'day'
            daily_schedule['shifts'].append({'nurse': nurse, 'shift': 'day'})
        
        # Evening 근무자 배정 (근무 횟수가 적고 day 근무에 포함되지 않은 간호사)
        available_evening_nurses = sorted([n for n in available_nurses if n not in day_nurses], key=lambda n: nurse_status[n]['evening_shifts'])
        evening_nurses = available_evening_nurses[:3]
        for nurse in evening_nurses:
            nurse_status[nurse]['total_shifts'] += 1
            nurse_status[nurse]['evening_shifts'] += 1
            nurse_status[nurse]['last_shift'] = 'evening'
            daily_schedule['shifts'].append({'nurse': nurse, 'shift': 'evening'})
        
        # Night 근무자 배정 (중간 그룹 우선, 그러나 제한 있음)
        available_night_nurses = sorted([n for n in available_nurses if n not in day_nurses and n not in evening_nurses], key=lambda n: nurse_status[n]['night_shifts'])
        
        # 중간 그룹 우선 배정, 그러나 night_shifts가 제한 이상 배정되지 않도록 함
        middle_group_night_nurses = [n for n in available_night_nurses if n in middle_group and nurse_status[n]['night_shifts'] < middle_group_night_limit][:2]
        night_nurses = middle_group_night_nurses

        # 중간 그룹에서 충분히 배정되지 않았을 경우, 다른 간호사에서 채움
        if len(night_nurses) < 2:
            remaining_nurses = [n for n in available_night_nurses if n not in night_nurses][:2 - len(night_nurses)]
            night_nurses.extend(remaining_nurses)

        for nurse in night_nurses:
            nurse_status[nurse]['total_shifts'] += 1
            nurse_status[nurse]['night_shifts'] += 1
            nurse_status[nurse]['last_shift'] = 'night'
            daily_schedule['shifts'].append({'nurse': nurse, 'shift': 'night'})

        return daily_schedule

    # 첫날은 랜덤 배정, 그 이후에는 근무 횟수가 적은 간호사 우선 배정
    for day_count in range(total_days):
        current_date = start_date + timedelta(days=day_count)
        available_nurses = [nurse for nurse in nurses if current_date not in vacation_days.get(nurse, [])]

        if day_count == 0:
            # 첫째 날 랜덤 배정
            daily_schedule = random_assign_first_day(current_date, available_nurses)
        else:
            # 2일차 이후 근무 횟수에 따른 배정
            daily_schedule = assign_from_second_day(current_date, available_nurses)

        schedule.append(daily_schedule)

    # 결과 출력
    for nurse, status in nurse_status.items():
        print(f"{nurse}: 총 근무 횟수 = {status['total_shifts']} (Day: {status['day_shifts']}, Evening: {status['evening_shifts']}, Night: {status['night_shifts']})")

    return schedule