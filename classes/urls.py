from django.urls import path
from . import views


urlpatterns = [
    path('create_school_class/', views.create_school_class),
    path('delete_school_class/<int:class_id>/', views.delete_school_class),
    path('get_class_teachers/<int:class_id>/', views.get_class_teachers),
    path('get_class_students/<int:class_id>/', views.get_class_students),
    path('get_school_classes/', views.get_school_classes),
    path('get_possible_class_masters/', views.get_possible_class_masters),
    path('get_school_class/<int:class_id>/', views.get_school_class),
    path('assign_class_master/<int:class_id>/<int:teacher_id>/',
         views.assign_class_master),
    path('assign_class_prefect/<int:class_id>/<str:student_id>/',
         views.assign_class_prefect),
    path('get_school_class_for_update/<int:class_id>/',
         views.get_school_class_for_update),
    path('update_school_class/<int:class_id>/', views.update_school_class),
    path('assign_class_master/<int:class_id>/<int:teacher_id>/',
         views.assign_class_master),
]
