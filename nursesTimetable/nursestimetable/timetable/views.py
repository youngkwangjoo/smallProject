from datetime import date
from django.shortcuts import render, redirect
from .forms import NurseForm
from .models import Nurse
from .utils import assign_shifts
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from .forms import OffDaysForm
from django.shortcuts import render

def nurse_input(request):
    if request.method == 'POST':
        form = NurseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('nurse_list')
    else:
        form = NurseForm()
    
    return render(request, 'nurse_input.html', {'form': form})

def generate_schedule(request):
    nurses = Nurse.objects.all()  # 간호사 리스트 가져오기
    start_date = date(2024, 10, 1)  # 예시 시작 날짜
    end_date = date(2024, 10, 30)  # 예시 종료 날짜

    # 공휴일 리스트 (예시)
    holidays = [
        date(2024, 10, 1),  # 예시 공휴일
        date(2024, 10, 5),  # 예시 공휴일
    ]

    # 사수-부사수 페어 설정
    senior_junior_pairs = []
    for nurse in nurses:
        if nurse.junior:  # junior가 있는 경우만 추가
            senior_junior_pairs.append((nurse, nurse.junior))
    
    # senior_junior_pairs가 비어 있는지 확인
    if not senior_junior_pairs:
        print("경고: 사수-부사수 페어가 존재하지 않습니다.")
    
    # 연차일 정보 준비 (예시)
    vacation_days = {}
    for nurse in nurses:
        vacation_days[nurse.id] = [leave_day.date for leave_day in nurse.leave_days.all()]

    if request.method == 'POST':
        form = OffDaysForm(request.POST)  # 폼을 통해 전달된 off day 값 받기
        if form.is_valid():
            total_off_days = form.cleaned_data['total_off_days']  # 입력된 총 off day 값
            # 변경된 assign_shifts 호출
            schedule = assign_shifts(nurses, start_date, end_date, holidays, senior_junior_pairs, vacation_days, total_off_days)

            # 매주 한 줄씩 달력에 넣기
            weeks = []
            week = []
            for day_schedule in schedule:
                if len(week) == 7:
                    weeks.append(week)
                    week = []
                week.append(day_schedule)
            if week:
                weeks.append(week)

            return render(request, 'calendar.html', {'schedule': weeks})
    else:
        form = OffDaysForm()  # GET 요청 시 빈 폼 생성

    return render(request, 'off_days_form.html', {'form': form})  # 폼을 템플릿으로 전달

def nurse_list(request):
    nurses = Nurse.objects.all()
    return render(request, 'nurse_list.html', {'nurses': nurses})

class NurseDeleteView(DeleteView):
    model = Nurse
    template_name = 'nurse_confirm_delete.html'
    success_url = reverse_lazy('nurse_list')  # 삭제 후 리다이렉트할 URL


