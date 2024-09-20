import random

def balance_nurse_shifts(nurse_status, schedule, total_work_days):
    """
    각 간호사의 총 근무 횟수를 총 근무일 수에 맞춰 조정하는 함수
    """
    # 부족한 근무 횟수를 먼저 채운다.
    for nurse, status in sorted(nurse_status.items(), key=lambda item: item[1]['total_shifts']):
        shift_needed = total_work_days - status['total_shifts']
        if shift_needed > 0:
            for day_schedule in schedule:
                if len(day_schedule['shifts']) < 3 and nurse not in [shift['nurse'] for shift in day_schedule['shifts']]:
                    day_schedule['shifts'].append({'nurse': nurse, 'shift': 'day'})
                    status['total_shifts'] += 1
                    shift_needed -= 1
                if shift_needed <= 0:
                    break

    # 초과된 근무 횟수를 줄인다.
    for nurse, status in sorted(nurse_status.items(), key=lambda item: item[1]['total_shifts'], reverse=True):
        shift_excess = status['total_shifts'] - total_work_days
        if shift_excess > 0:
            for day_schedule in schedule:
                if nurse in [shift['nurse'] for shift in day_schedule['shifts']]:
                    day_schedule['shifts'] = [shift for shift in day_schedule['shifts'] if shift['nurse'] != nurse]
                    status['total_shifts'] -= 1
                    shift_excess -= 1
                if shift_excess <= 0:
                    break


def balance_shift_types(nurse_status, schedule):
    """
    근무 종류별로 간호사에게 균등하게 배정되도록 하는 함수.
    day, evening, night 근무의 균형을 맞춥니다.
    """
    for nurse, status in nurse_status.items():
        day_count = status.get('day_shifts', 0)
        evening_count = status.get('evening_shifts', 0)
        night_count = status.get('night_shifts', 0)

        # 최소 및 최대 근무 횟수 찾기
        min_shifts = min(day_count, evening_count, night_count)
        max_shifts = max(day_count, evening_count, night_count)

        # 간호사의 시프트별 불균형이 큰 경우, 조정하여 균형을 맞춤
        for day_schedule in schedule:
            for shift in day_schedule['shifts']:
                if shift['nurse'] == nurse:
                    shift_type = shift['shift']
                    
                    # night 시프트가 적을 경우 해당 간호사에게 night 시프트 할당
                    if night_count < min_shifts + 1 and shift_type != 'night':
                        shift['shift'] = 'night'
                        night_count += 1
                        if shift_type == 'day':
                            day_count -= 1
                        elif shift_type == 'evening':
                            evening_count -= 1

                    # evening 시프트가 적을 경우 해당 간호사에게 evening 시프트 할당
                    elif evening_count < min_shifts + 1 and shift_type != 'evening':
                        shift['shift'] = 'evening'
                        evening_count += 1
                        if shift_type == 'day':
                            day_count -= 1
                        elif shift_type == 'night':
                            night_count -= 1

        # 업데이트된 shift 카운트 저장
        nurse_status[nurse]['day_shifts'] = day_count
        nurse_status[nurse]['evening_shifts'] = evening_count
        nurse_status[nurse]['night_shifts'] = night_count