from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/years/', include('years.urls')),
    path('api/v1/terms/', include('terms.urls')),
    path('api/v1/sequences/', include('sequences.urls')),
    path('api/v1/departments/', include('departments.urls')),
    path('api/v1/teachers/', include('teachers.urls')),
    path('api/v1/school_classes/', include('classes.urls')),
    path('api/v1/subjects/', include('subjects.urls')),
    path('api/v1/students/', include('students.urls')),
    path('api/v1/marks/', include('marks.urls')),
    path('api/v1/absences/', include('absences.urls')),
    path('api/v1/others/', include('others.urls')),
]
