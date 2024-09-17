from django import forms
from .models import Nurse

class NurseForm(forms.ModelForm):
    class Meta:
        model = Nurse
        fields = ['name', 'is_senior', 'leave_days']
