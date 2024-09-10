from django.urls import path

from .views import (
    create_teacher,
    delete_teacher,
    get_all_teachers,
    get_teacher,
    update_teacher,
    teacher_password_change,
    change_teacher_image,
    load_teacher,
    LogoutTeacher,
    LogoutTeacherAll,
    login_teacher,
    get_just_teacher_info,
    get_teacher_classes,
    get_teacher_subjects_in_a_class
)

urlpatterns = [
    path('get_all_teachers/', get_all_teachers),
    path('create_teacher/<int:department_id>/', create_teacher),
    path('get_teacher/<int:teacher_id>/', get_teacher),
    path('get_just_teacher_info/<int:teacher_id>/', get_just_teacher_info),
    path('delete_teacher/<int:teacher_id>/', delete_teacher),
    path('teacher_password_change/<int:teacher_id>/', teacher_password_change),
    path('update_teacher/<int:teacher_id>/<int:new_department_id>/', update_teacher),
    path("change_teacher_image/<int:teacher_id>/", change_teacher_image),
    path('load_teacher/', load_teacher),
    path('login_teacher/', login_teacher),
    path('logout_teacher/', LogoutTeacher.as_view()),
    path('logout_teacher_all/', LogoutTeacherAll.as_view()),
    path('get_teacher_classes/<int:teacher_id>/', get_teacher_classes),
    path('get_teacher_subjects_in_a_class/<int:teacher_id>/<int:class_id>/',
         get_teacher_subjects_in_a_class),
]
