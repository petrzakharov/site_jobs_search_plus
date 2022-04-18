from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('/vacancies', views.vacancies_list, name='vacancies_list'),
    path('/vacancies/cat/<str:frontend>/', views.category, name='category'),
    path('/companies/<int:company_id>', views.about_company, name='company'),
    path('/vacancies/<int:vacancy_id', views.vacancy, name='vacancy')
]
