from django.urls import path
from timetable import views
from .views import NurseDeleteView

urlpatterns = [
    path('', views.nurse_list, name='nurse_list'),  # 기본 경로는 간호사 목록
    path('input/', views.nurse_input, name='nurse_input'),  # 간호사 입력 페이지
    path('schedule/', views.generate_schedule, name='generate_schedule'),  # 스케줄 생성 페이지
    path('delete/<int:pk>/', NurseDeleteView.as_view(), name='nurse_delete'),  # 간호사 삭제 페이지
]
