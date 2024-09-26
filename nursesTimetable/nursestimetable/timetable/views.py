from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .serializers import NurseSerializer
from .models import Nurse
from .utils.shift import assign_shifts
import json

@csrf_exempt  # 이 데코레이터를 추가하여 CSRF 검증 비활성화
def generate_schedule(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # 프론트엔드로부터 간호사 목록, 연차, 달력 정보 받아옴
        nurse_list = data.get('nurses', [])
        total_off_days = int(data.get('total_off_days', 0))
        total_work_days = int(data.get('total_work_days', 0))
        total_days = int(data.get('total_days', 0))  # 한 달의 총 일수
        start_weekday = data.get('start_weekday', '')  # 시작 요일

        # 간호사 객체 생성 및 연차 정보 처리
        nurses = []
        vacation_days = {}
        for nurse_data in nurse_list:
            nurse, created = Nurse.objects.get_or_create(
                id=nurse_data['id'],
                defaults={
                    'name': nurse_data['name'],
                    'is_senior': nurse_data['is_senior']
                }
            )
            vacation_days[str(nurse.id)] = nurse_data.get('vacation_days', [])
            nurses.append(nurse)

        # 요일을 숫자로 변환 (0: Monday, 6: Sunday)
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        start_day_index = weekdays.index(start_weekday)

        # 동적으로 한 달의 날짜 생성
        start_date = datetime(2024, 10, 1).date()  # 이 부분은 원래의 1일 날짜, 2024년 10월을 예시로 사용
        end_date = start_date + timedelta(days=total_days - 1)  # 총 일수를 기준으로 마지막 날짜 계산

        holidays = []  # 별도 휴일 정보가 없다면 비워두기

        # 스케줄 생성
        schedule = assign_shifts(nurses, start_date, end_date, holidays, vacation_days, total_off_days, total_work_days)

        # 근무 상태 집계 및 콘솔 출력
        nurse_status = {nurse: {
            'total_shifts': 0,
            'day_shifts': 0,
            'evening_shifts': 0,
            'night_shifts': 0
        } for nurse in nurses}

        for day_schedule in schedule:
            for shift in day_schedule['shifts']:
                nurse = shift['nurse']
                shift_type = shift['shift']

                nurse_status[nurse]['total_shifts'] += 1
                if shift_type == 'day':
                    nurse_status[nurse]['day_shifts'] += 1
                elif shift_type == 'evening':
                    nurse_status[nurse]['evening_shifts'] += 1
                elif shift_type == 'night':
                    nurse_status[nurse]['night_shifts'] += 1

        # 콘솔 출력
        for nurse, status in nurse_status.items():
            print(f"{nurse}: 총 근무 횟수 = {status['total_shifts']} (Day: {status['day_shifts']}, Evening: {status['evening_shifts']}, Night: {status['night_shifts']})")

        # 스케줄 데이터를 JSON으로 변환하여 반환
        schedule_data = []
        for day_schedule in schedule:
            day_data = {
                'date': day_schedule['date'],
                'shifts': [
                    {'nurse': NurseSerializer(shift['nurse']).data, 'shift': shift['shift']}
                    for shift in day_schedule['shifts']
                ]
            }
            schedule_data.append(day_data)

        return JsonResponse(schedule_data, safe=False)

    return JsonResponse({'error': 'Invalid request'}, status=400)



@csrf_exempt
def delete_nurses(request):
    if request.method == 'DELETE':
        # 모든 간호사를 삭제
        Nurse.objects.all().delete()
        return JsonResponse({'message': 'All nurses deleted successfully'}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)

