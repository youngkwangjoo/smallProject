from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # 관리자 페이지
    path('nurses/', include('timetable.urls')),  # timetable 앱의 URL 패턴 포함
]
