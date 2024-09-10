from django.urls import path

from . import views

urlpatterns = [
    path('get_all_students_in_class/<class_id>/',
         views.get_all_students_in_class),
    path('create_student/<int:class_id>/', views.create_student),
    path('change_student_image/<str:student_id>/', views.change_student_image),
    path('get_student/<str:student_id>/', views.get_student),
    path('delete_student/<str:student_id>/', views.delete_student),
    path('update_student/<str:student_id>/<int:class_id>/', views.update_student),
    path('get_all_students_in_given_year/<int:year_id>/',
         views.get_all_students_in_given_year),
    path('get_all_students_in_school/', views.get_all_students_in_school),
    path("get_student_for_update/<str:student_id>/",
         views.get_student_for_update),
]
