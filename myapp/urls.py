from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path(
        '/vacancies',
        views.VacanciesList.as_view(),
        name='vacancies_list'
    ),
    path(
        '/vacancies/cat/<str:frontend>/',
        views.VacanciesBySpecialty,
        name='specialty'
    ),
    path(
        '/companies/<int:company_id>',
        views.Company.as_view(),
        name='company'
    ),
    path(
        '/vacancies/<int:vacancy_id',
        views.Vacancy.as_view(),
        name='vacancy'
    ),
]
