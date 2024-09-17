from django.urls import path
from schedule.views import NurseDeleteView  # 'scheduler' 앱의 views 모듈에서 NurseDeleteView를 가져옵니다.
from schedule import views

urlpatterns = [
    path('nurses/', views.nurse_input, name='nurse_input'),
    path('nurses/list/', views.nurse_list, name='nurse_list'),
    path('schedule/', views.generate_schedule, name='generate_schedule'),
    path('nurses/delete/<int:pk>/', NurseDeleteView.as_view(), name='nurse_delete'),
]
