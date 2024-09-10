from django.urls import path

from .views import (
    create_year,
    get_year,
    update_year,
    delete_year,
    get_years,
    deactivate_year
)


urlpatterns = [
    path('create_year/', create_year),
    path('get_years/', get_years),
    path('get_year/<int:year_id>/', get_year),
    path('update_year/<int:year_id>/', update_year),
    path('delete_year/<int:year_id>/', delete_year),
    path('deactivate_year/', deactivate_year),
]
