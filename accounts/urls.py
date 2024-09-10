from django.urls import path

from . import views


urlpatterns = [
    path('change_admin_password/<int:admin_id>/', views.change_admin_password),
    path('change_admin_image/<int:admin_id>/', views.change_admin_image),
    path('create_admin_user/', views.create_admin_user),
    path('delete_admin/<int:admin_id>/', views.delete_admin),
    path('load_admin/', views.load_admin),
    path('login_admin_user/', views.login_admin_user),
    path('logout_admin/', views.LogoutAdmin.as_view()),
    path('logout_all_admin/', views.LogoutAllAdmin.as_view()),
    path('get_admin_user/<int:admin_id>/', views.get_admin_user),
    path('get_all_admin_users/', views.get_all_admin_users),
    path('update_admin/<int:admin_id>/', views.update_admin),
    path('get_just_admin_info/<int:admin_id>/', views.get_just_admin_info)
]
