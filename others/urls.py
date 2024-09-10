from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard),
    path('search/', views.search),
    path('get_class_statistics_for_a_subject/<int:class_id>/<int:subject_id>/<int:sequence_id>/',
         views.get_class_statistics_for_a_subject),
]
