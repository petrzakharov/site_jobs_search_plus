from django.urls import path

from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path(
        'vacancies/',
        views.VacanciesList.as_view(),
        name='vacancies_list'
    ),
    path(
        'vacancies/cat/<str:specialty>/',
        views.VacanciesBySpecialty.as_view(),
        name='specialty'
    ),
    path(
        'companies/<int:company_id>',
        views.Company.as_view(),
        name='company'
    ),
    path(
        'vacancies/<int:vacancy_id>',
        views.Vacancy.as_view(),
        name='vacancy'
    ),
]
