from django.urls import path

from . import views

urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("vacancies/", views.VacanciesList.as_view(), name="vacancies_list"),
    path(
        "vacancies/cat/<str:specialty>/",
        views.VacanciesBySpecialty.as_view(),
        name="specialty",
    ),
    path("companies/<int:company_id>", views.Company.as_view(), name="company"),
    path("vacancies/<int:vacancy_id>", views.Vacancy.as_view(), name="vacancy"),
    path(
        "vacancies/<int:vacancy_id>/send/",
        views.VacancySend.as_view(),
        name="vacancy_send",
    ),
    path("mycompany/", views.MyCompany.as_view(), name="my_company"),
    path(
        "mycompany/letsstart/",
        views.MyCompanyStart.as_view(),
        name="my_company_start",
    ),
    path(
        "mycompany/create/",
        views.MyCompanyCreate.as_view(),
        name="my_company_create",
    ),
    path(
        "mycompany/vacancies/",
        views.MyCompanyVacanciesList.as_view(),
        name="my_company_vacancies_list",
    ),
    path(
        "mycompany/vacancies/create/",
        views.MyCompanyVacanciesCreate.as_view(),
        name="my_company_vacancies_create",
    ),
    path(
        "mycompany/vacancies/<int:vacancy_id>",
        views.MyCompanyVacancy.as_view(),
        name="my_company_vacancy",
    ),
    path(
        "search/",
        views.SearchView.as_view(),
        name="search",
    ),
    path(
        "myresume/letsstart/",
        views.LetsCreateResume.as_view(),
        name="lets_create_resume",
    ),
    path(
        "myresume/create/",
        views.MyResumeCreate.as_view(),
        name="my_resume_create",
    ),
    path("myresume/", views.MyResume.as_view(), name="my_resume"),
]
