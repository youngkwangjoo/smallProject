from django import forms
from .models import Nurse

class NurseForm(forms.ModelForm):
    class Meta:
        model = Nurse
        fields = ['name', 'is_senior', 'leave_days']

class OffDaysForm(forms.Form):
    total_off_days = forms.IntegerField(label='총 Off 날 수', min_value=0)
    total_work_days = forms.IntegerField(label='근무일 수', min_value=0)
