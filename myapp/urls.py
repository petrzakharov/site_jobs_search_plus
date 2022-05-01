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
        name="vacancy_send",  # сюда приходит post запрос со страницы вакансии с откликом
        # просто создаем связь в двух моделях и рисуем что-то в шаблоне?
        #
    ),
    path(
        "mycompany/",
        views.MyCompany.as_view(),
        name="my_company"
        # Если компания есть рендерит шаблон company_edit, если нет переадресует на шаблон company_create
        # context ok
    ),
    path(
        "mycompany/letsstart/",
        views.MyComapanyStart.as_view(),
        name="my_company_start",
        # context ok
    ),
    path(
        "mycompany/create/",
        views.MyComapanyCreate.as_view(),
        name="my_company_create",  # Моя компания (пустая форма)
        # проверяем что у юзера нет компании, если есть переадресуем на mycompany,
        # если нет то возвраещем пустую форму
        # context ok
    ),
    path(
        "mycompany/vacancies/",
        views.MyCompanyVacanciesList.as_view(),
        name="my_company_vacancies_list",  # Мои вакансии (список)
        # обычная вьюха, возвращаем все вакансии по моей компании
        # добавить в context количество откликов через annotate
    ),
    path(
        "mycompany/vacancies/create/",
        views.MyComapnyVacanciesCreate.as_view(),
        name="my_company_vacancies_create",  # Мои вакансии (пустая форма)
        # проверяем что у юзера есть компания, возвращаем форму на создание вакансии
    ),
    path(
        "mycompany/vacancies/<int:vacancy_id>",
        views.MyCompanyVacancy.as_view(),
        name="my_company_vacancy",  # Одна моя вакансия (заполненная форма)
        # принимает post запрос с /mycompany/vacancies/create/
        # добавить в context количество откликов через annotate
        # вывести отклики
    ),
    ##### вторая часть
    # path(
    #     "/myresume/letsstart/",
    #     views.LetsCreateResume.as_view(),
    #     name="lets_create_resume",  # Резюме не создано - предложение создать
    # ),
    # path(
    #     "/myresume/create/",
    #     views.MyResumeCreate.as_view(),
    #     name="my_resume_create",  # Создание резюме (пустая форма)
    # ),
    # path(
    #     "/myresume/", views.MyResume.as_view(), name="my_resume"
    # ),  # Мое резюме (заполненная форма)
]
