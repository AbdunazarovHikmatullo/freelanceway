from django.urls import path
from . import views

urlpatterns = [
    path('', views.vacancies_list, name='vacancies_list'),
    path('<int:vacancy_id>/', views.vacancy_detail, name='vacancy_detail'),
    path('create/', views.create_vacancy, name='create_vacancy'),
    path('<int:vacancy_id>/edit/', views.edit_vacancy, name='edit_vacancy'),
    path('<int:vacancy_id>/delete/', views.delete_vacancy, name='delete_vacancy'),
    path('<int:vacancy_id>/apply/', views.apply_to_vacancy, name='apply_to_vacancy'),
    path('my-vacancies/', views.my_vacancies, name='my_vacancies'),
    path('<int:vacancy_id>/applications/', views.vacancy_applications, name='vacancy_applications'),
    path('application/<int:application_id>/status/<str:status>/', views.update_application_status, name='update_application_status'),
    path('my-applications/', views.my_applications, name='my_applications'),
]