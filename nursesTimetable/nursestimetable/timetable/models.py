from django.db import models

class Nurse(models.Model):
    name = models.CharField(max_length=100)  # 간호사 이름
    is_senior = models.BooleanField(default=False)  # 사수 여부
    leave_days = models.ManyToManyField('LeaveDay', blank=True)  # 연차일

class LeaveDay(models.Model):
    date = models.DateField()  # 연차 날짜

class Shift(models.Model):
    DAY = 'day'
    EVENING = 'evening'
    NIGHT = 'night'
    OFF = 'off'
    
    SHIFT_CHOICES = [
        (DAY, 'Day (07:00 - 15:00)'),
        (EVENING, 'Evening (14:30 - 22:30)'),
        (NIGHT, 'Night (22:00 - 07:30)'),
        (OFF, 'Off'),
    ]
    
    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE)  # 근무 간호사
    date = models.DateField()  # 근무 날짜
    shift_type = models.CharField(max_length=10, choices=SHIFT_CHOICES)  # 근무 종류
