from django.db.models import Count
from django.http import HttpResponseNotFound, HttpResponseServerError
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView

from . import models


def custom_handler404(request, exception):  # Проверить, отрабатывает ли этот хендлер с классами
    return HttpResponseNotFound('<h1>Страница не найдена, упс!</h1>')


def custom_handler500(request):  # Проверить, отрабатывает ли этот хендлер с классами
    return HttpResponseServerError('<h1>Произошла ошибка на сервере, упс!</h1>')


# во всех вьюхи добавить кнопки назад и меню (подумать как лучше)

class Index(TemplateView):  
    # проверить количество запросов с помощью джанго тулбар
    template_name = 'myapp/index_temp.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vacancies'] = models.Vacancy.objects.values(
            'specialty__title', 'specialty__code').annotate(count=Count('id')
        )
        context['companies'] = models.Company.objects.values(
            'logo', 'id').annotate(count=Count('vacancies'))
        return context


class VacanciesList(ListView):
    model = models.Vacancy
    template_name = 'myapp/vacancies_temp.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_vacancie'] = True
        return context
    # заменить запятые точками в шаблоне, написать кастомный фильтр
    # добавить разделение разрядов в зарплате
    # русифицировать формат даты "11 марта"


class VacanciesBySpecialty(ListView):
    template_name = 'myapp/vacancies_temp.html'
    allow_empty = False

    def get_queryset(self):
        return models.Vacancy.objects.filter(specialty__code=self.kwargs['specialty'])


class Vacancy(DetailView):
    model = models.Vacancy
    template_name = 'myapp/vacancy_temp.html'
    pk_url_kwarg = 'vacancy_id'
    context_object_name = 'vacancy'
    # Возможно имеет смысл сделать select related с Company
    # добавить разделение разрядов в зарплате
    # заменить запятые точками в шаблоне, написать кастомный фильтр


class Company(ListView):
    model = models.Vacancy
    template_name = 'myapp/company_temp.html'
    pk_url_kwarg = 'company_id'

    def get_queryset(self):
        return models.Vacancy.objects.filter(company__id=self.kwargs['company_id'])
    # добавить разделение разрядов в зарплате
    # заменить запятые точками в шаблоне, написать кастомный фильтр
    # русифицировать формат даты "11 марта"
    # вызывать 404 не при пустом списке, а если такой компании нет в бд
    # добавить в контекст get_object_or_404 + данные о компании (решит предыдущий вопрос)
    
