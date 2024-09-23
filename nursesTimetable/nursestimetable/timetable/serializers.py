# serializers.py
from rest_framework import serializers
from .models import Nurse, Shift

class NurseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nurse
        fields = ['id', 'name', 'is_senior', 'leave_days']

class ShiftSerializer(serializers.ModelSerializer):
    nurse = NurseSerializer()

    class Meta:
        model = Shift
        fields = ['nurse', 'date', 'shift_type']
