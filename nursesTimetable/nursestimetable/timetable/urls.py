from django.urls import path
from timetable import views
from .views import NurseDeleteView

urlpatterns = [
    path('nurses/', views.nurse_input, name='nurse_input'),
    path('nurses/list/', views.nurse_list, name='nurse_list'),  # nurse_list 경로 추가
    path('schedule/', views.generate_schedule, name='generate_schedule'),
    path('nurses/delete/<int:pk>/', NurseDeleteView.as_view(), name='nurse_delete'),
    
]
