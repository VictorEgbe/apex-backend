from django.urls import path

from . import views

urlpatterns = [
    path('get_marks_for_student/<str:student_id>/', views.get_marks_for_student),
    path('create_or_update_mark/<int:class_id>/<int:subject_id>/',
         views.create_or_update_mark),
    path('get_student_list_in_class_for_marks_input/<int:class_id>/<int:subject_id>/',
         views.get_student_list_in_class_for_marks_input)
]
