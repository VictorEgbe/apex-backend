from django.urls import path

from . import views

urlpatterns = [
    path('create_or_update_students_absences/',
         views.create_or_update_students_absences),
    path('get_total_sequence_absences/<str:student_id>/<int:sequence_id>/',
         views.get_total_sequence_absences),
    path('get_total_term_absences/<str:student_id>/<int:term_id>/',
         views.get_total_term_absences),

    path('create_or_update_teachers_absences/<int:teacher_id>/',
         views.create_or_update_teachers_absences),
]
