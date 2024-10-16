from django.urls import path
from timetable import views
from .views import delete_nurses
from .views import calculate_min_nurses_view

urlpatterns = [
    path('generate_schedule/', views.generate_schedule, name='generate_schedule'),  # 스케줄 생성 API
    path('nurses/delete/', delete_nurses, name='delete_nurses'),
    path('calculate_min_nurses/', calculate_min_nurses_view, name='calculate_min_nurses'),
    
]
