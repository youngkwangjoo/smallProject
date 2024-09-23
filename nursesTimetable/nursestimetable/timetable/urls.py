from django.urls import path
from timetable import views


urlpatterns = [
    path('generate_schedule/', views.generate_schedule, name='generate_schedule'),  # 스케줄 생성 API
]
