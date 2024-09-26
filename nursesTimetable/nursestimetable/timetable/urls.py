from django.urls import path
from timetable import views
from .views import delete_nurse


urlpatterns = [
    path('generate_schedule/', views.generate_schedule, name='generate_schedule'),  # 스케줄 생성 API
        path('delete-nurse/', delete_nurse, name='delete_nurse'),
]
