from django.http import HttpResponseNotFound, HttpResponseServerError
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView

from . import models


def custom_handler404(request, exception): # нужен ли хендлер если использую классы?
    return HttpResponseNotFound('<h1>Страница не найдена, упс!</h1>')


def custom_handler500(request): # нужен ли хендлер если использую классы?
    return HttpResponseServerError('<h1>Произошла ошибка на сервере, упс!</h1>')


class Index(TemplateView):  # от чего наследуем?
    template_name = 'myapp/index_temp.html'

    def get_context_data(self, **kwargs):
        pass


class VacanciesList(ListView):
    model = models.Vacancy
    template_name = 'myapp/vacancies_temp.html'


class VacanciesBySpecialty(TemplateView): # от чего наследуем?
    template_name = 'myapp/vacancies_temp.html'


class Vacancy(DetailView):
    model = models.Vacancy
    template_name = 'myapp/vacancy_temp.html'


class Company(TemplateView):
    #model = models.Company
    template_name = 'myapp/company_temp.html'
