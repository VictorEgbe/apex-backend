from django.urls import path
from . import views


urlpatterns = [
    path('get_all_subjects/', views.get_all_subjects),
    path('get_single_subject/<int:subject_id>/', views.get_single_subject),
    path('create_subject/', views.create_subject),
    path('get_all_subjects_by_a_teacher/<int:teacher_id>/',
         views.get_all_subjects_by_a_teacher),
    path('delete_subject/<int:subject_id>/', views.delete_subject),
    path('update_subject/<int:subject_id>/', views.update_subject),
    path('add_teacher_to_subject/<int:subject_id>/<int:teacher_id>/',
         views.add_teacher_to_subject),
    path('remove_teacher_to_subject/<int:subject_id>/<int:teacher_id>/',
         views.remove_teacher_to_subject),
]
