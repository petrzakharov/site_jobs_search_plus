from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView

from . import models


class Index(TemplateView):
    template_name = 'myapp/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['specialties'] = models.Specialty.objects.annotate(
            count=Count('vacancies'))
        context['companies'] = models.Company.objects.values(
            'logo', 'id').annotate(count=Count('vacancies'))
        return context


class VacanciesList(ListView):
    model = models.Vacancy
    template_name = 'myapp/vacancies.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_vacancie'] = True
        return context

    def get_queryset(self):
        return models.Vacancy.objects.select_related('company')


class VacanciesBySpecialty(ListView):
    template_name = 'myapp/vacancies.html'
    allow_empty = False

    def get_queryset(self):
        return models.Vacancy.objects.filter(
            specialty__code=self.kwargs['specialty']
        ).select_related('company')


class Vacancy(DetailView):
    model = models.Vacancy
    template_name = 'myapp/vacancy.html'
    pk_url_kwarg = 'vacancy_id'
    context_object_name = 'vacancy'


class Company(ListView):

    # Как можно оптимизировать эту вьюху, чтобы сделать меньше запросов?

    model = models.Vacancy
    template_name = 'myapp/company.html'
    pk_url_kwarg = 'company_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = get_object_or_404(models.Company,
                                               id=self.kwargs['company_id'])
        return context

    def get_queryset(self):
        return models.Vacancy.objects.filter(
            company__id=self.kwargs['company_id']
        ).select_related('company')
