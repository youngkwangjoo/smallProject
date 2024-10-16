from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .serializers import NurseSerializer
from .models import Nurse
from .utils.shift import assign_shifts
import json
from .utils.calculate import calculate_min_nurses
from .utils.common import get_weekends


@csrf_exempt
def generate_schedule(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"Received data: {data}")  # 요청 데이터를 출력하여 확인
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        # 프론트엔드로부터 데이터 추출
        nurse_list = data.get('nurses', [])
        total_off_days = int(data.get('total_off_days', 0))
        total_work_days = int(data.get('total_work_days', 0))
        total_days = int(data.get('total_days', 0))
        start_weekday = data.get('start_weekday', '')

        print(f"Total Days: {total_days}, Start Weekday: {start_weekday}")  # 추출된 데이터 확인

        # 간호사 객체 생성 및 휴가 정보 처리
        nurses = []
        vacation_days = {}
        nurse_info_dict = {}  # 간호사 정보 딕셔너리로 저장
        for nurse_data in nurse_list:
            nurse, created = Nurse.objects.get_or_create(
                id=nurse_data['id'],
                defaults={
                    'name': nurse_data['name'],
                    'is_senior': nurse_data['is_senior']
                }
            )
            print(f"Nurse processed: {nurse.name}, Senior: {nurse.is_senior}")  # 간호사 정보 확인

            vacation_days[str(nurse.id)] = nurse_data.get('vacation_days', [])
            nurse_info = {
                'id': nurse.id,
                'name': nurse.name,
                'is_senior': nurse.is_senior,
                'vacation_days': vacation_days[str(nurse.id)]
            }
            nurses.append(nurse_info)
            nurse_info_dict[nurse.id] = nurse_info  # 간호사 ID를 키로 해서 간호사 정보 저장

        # 스케줄 생성
        try:
            schedule = assign_shifts(nurses, total_days, [], vacation_days, total_off_days, total_work_days, start_weekday)
        except Exception as e:
            print(f"Error during scheduling: {str(e)}")  # 스케줄 생성 중 에러 로그

        # 간호사 상세 정보를 포함하여 schedule 데이터를 변환
        schedule_with_details = []
        for day_schedule in schedule:
            day_data = {
                'date': day_schedule['date'],
                'shifts': [
                    {
                        'nurse': {
                            'id': nurse_info_dict[shift['nurse']]['id'],
                            'name': nurse_info_dict[shift['nurse']]['name'],
                            'is_senior': nurse_info_dict[shift['nurse']]['is_senior'],
                        },
                        'shift': shift['shift']
                    }
                    for shift in day_schedule['shifts']
                ]
            }
            schedule_with_details.append(day_data)
 # 최종 스케줄 확인

        return JsonResponse(schedule_with_details, safe=False)

    return JsonResponse({'error': 'Invalid request'}, status=400)



@csrf_exempt
def delete_nurses(request):
    if request.method == 'OPTIONS':  # Preflight 요청 처리
        response = JsonResponse({'message': 'Preflight request successful'})
        response['Access-Control-Allow-Origin'] = 'https://www.schdule.site'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        return response
    
    if request.method == 'DELETE':
        # 간호사 삭제 로직
        Nurse.objects.all().delete()
        return JsonResponse({'message': 'All nurses deleted successfully'}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def calculate_min_nurses_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        try:
            # POST 요청에서 데이터 추출
            total_days = data.get('total_days', 0)
            total_off_days = data.get('total_off_days', 0)
            total_work_days = data.get('total_work_days', 0)
            start_weekday = data.get('start_weekday', '')  # start_weekday 추가
            nurses_data = data.get('nurses', [])

            # nurses 리스트에서 필요한 정보를 추출하여 사용
            nurses = [
                {
                    'id': nurse['id'],
                    'is_senior': nurse['is_senior'],
                    'vacation_days': nurse.get('vacation_days', [])
                }
                for nurse in nurses_data
            ]

            # 최소 간호사 수 계산
            min_nurses_needed = calculate_min_nurses(total_days, total_off_days, total_work_days, start_weekday, nurses)

            return JsonResponse({'min_nurses_needed': min_nurses_needed}, status=200)
        except Exception as e:
            # 에러 발생 시 예외 처리
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
