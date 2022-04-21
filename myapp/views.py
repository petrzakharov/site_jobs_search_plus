from django.http import HttpResponseNotFound, HttpResponseServerError
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView

from . import models


def custom_handler404(request, exception):  # Проверить, отрабатывает ли этот хендлер с классами
    return HttpResponseNotFound('<h1>Страница не найдена, упс!</h1>')


def custom_handler500(request):  # Проверить, отрабатывает ли этот хендлер с классами
    return HttpResponseServerError('<h1>Произошла ошибка на сервере, упс!</h1>')


class Index(TemplateView):  # от чего наследуем?
    template_name = 'myapp/index_temp.html'

    def get_context_data(self, **kwargs):
        pass
        # К Specialty модели добавить annotat'ом количество вакансий
        # К Company добавить annotate количество вакансий, с помощью values убрать ненужные поля


class VacanciesList(ListView):
    model = models.Vacancy
    template_name = 'myapp/vacancies_temp.html'


class VacanciesBySpecialty(ListView):
    template_name = 'myapp/vacancies_temp.html'
    # Переопределить get_queryset() в котором взять из юрл название специальности и по нему отфильтровать кверисет
    # Использовать get_list_or_404() для ситуации когда передана несуществующая специализация удовлетворяющая нашему пути


class Vacancy(DetailView):
    model = models.Vacancy
    template_name = 'myapp/vacancy_temp.html'
    # Использовать get_object_or_404


class Company(ListView):
    model = models.Vacancy
    template_name = 'myapp/company_temp.html'
    # Переопределить get_queryset(), взять из юрл название компании и отфильровать по нему таблицу вакансий
    # Переопределить get_context_data() добавить данные о компании, сделать count() вакансий
    # # Использовать get_object_or_404 когда передана несуществующее название компании в модели
