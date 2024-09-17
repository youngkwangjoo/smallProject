from django.shortcuts import render, redirect
from .forms import NurseForm
from .models import Nurse, Shift
from .utils import assign_shifts
from datetime import date
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from .models import Nurse

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
    
    schedule = assign_shifts(nurses, start_date, end_date)

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


def nurse_list(request):
    nurses = Nurse.objects.all()
    return render(request, 'nurse_list.html', {'nurses': nurses})

class NurseDeleteView(DeleteView):
    model = Nurse
    template_name = 'nurse_confirm_delete.html'
    success_url = reverse_lazy('nurse_list')  # 삭제 후 리다이렉트할 URL