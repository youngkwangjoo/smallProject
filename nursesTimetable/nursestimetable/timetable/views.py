from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .serializers import NurseSerializer
from .models import Nurse
from .utils.shift import assign_shifts
import json

@csrf_exempt
def generate_schedule(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        # 프론트엔드로부터 데이터 추출
        nurse_list = data.get('nurses', [])
        total_off_days = int(data.get('total_off_days', 0))
        total_work_days = int(data.get('total_work_days', 0))
        total_days = int(data.get('total_days', 0))
        start_weekday = data.get('start_weekday', '')

        # 간호사 객체 생성 및 휴가 정보 처리
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
            nurses.append({
                'id': nurse.id,
                'name': nurse.name,
                'is_senior': nurse.is_senior,
                'vacation_days': vacation_days[str(nurse.id)]
            })

        # 스케줄 생성
        schedule = assign_shifts(nurses, total_days, [], vacation_days, total_off_days, total_work_days, start_weekday)

        return JsonResponse(schedule, safe=False)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def delete_nurses(request):
    if request.method == 'DELETE':
        # 모든 간호사를 삭제
        Nurse.objects.all().delete()
        return JsonResponse({'message': 'All nurses deleted successfully'}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)

