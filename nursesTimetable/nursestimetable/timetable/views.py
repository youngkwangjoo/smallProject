from datetime import date
from django.shortcuts import render, redirect
from .forms import NurseForm
from .models import Nurse
from .utils.shift import assign_shifts  # shift 모듈에서 assign_shifts 함수 가져오기
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from .forms import OffDaysForm
import random  # 랜덤 페어링을 위해 import

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
    nurses = Nurse.objects.all()
    start_date = date(2024, 10, 1)
    end_date = date(2024, 10, 31)

    holidays = [
        date(2024, 10, 1),
        date(2024, 10, 5),
    ]

    vacation_days = {}
    for nurse in nurses:
        vacation_days[nurse.id] = [leave_day.date for leave_day in nurse.leave_days.all()]

    if request.method == 'POST':
        form = OffDaysForm(request.POST)
        if form.is_valid():
            total_off_days = form.cleaned_data['total_off_days']
            total_work_days = form.cleaned_data['total_work_days']  # 근무일 수 가져오기
            
            # 사수-부사수 페어링을 동적으로 처리 (랜덤 페어링)
            seniors = [nurse for nurse in nurses if nurse.is_senior]
            juniors = [nurse for nurse in nurses if not nurse.is_senior]
            senior_junior_pairs = []

            # 페어링이 필요한 만큼 랜덤으로 사수와 부사수를 짝짓기
            while juniors and seniors:
                junior = random.choice(juniors)
                senior = random.choice(seniors)
                senior_junior_pairs.append((senior, junior))
                juniors.remove(junior)
                seniors.remove(senior)

            # assign_shifts로 스케줄 생성
            schedule = assign_shifts(nurses, start_date, end_date, holidays, vacation_days, total_off_days, total_work_days)

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
        form = OffDaysForm()

    return render(request, 'off_days_form.html', {'form': form})


def nurse_list(request):
    nurses = Nurse.objects.all()
    return render(request, 'nurse_list.html', {'nurses': nurses})

class NurseDeleteView(DeleteView):
    model = Nurse
    template_name = 'nurse_confirm_delete.html'
    success_url = reverse_lazy('nurse_list')  # 삭제 후 리다이렉트할 URL
