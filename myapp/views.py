from calendar import c

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView

from . import models
from .forms import ApplicationForm, CompanyForm, VacancyForm
from .permissions import (
    UserMustHasCompany,
    UserMustHasNotCompany,
    UserViewOnlyYourVacancies,
)


class Index(TemplateView):
    template_name = "myapp/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["specialties"] = models.Specialty.objects.annotate(
            count=Count("vacancies")
        )
        context["companies"] = models.Company.objects.values("logo", "id").annotate(
            count=Count("vacancies")
        )
        return context


class VacanciesList(ListView):
    model = models.Vacancy
    template_name = "myapp/vacancies.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_vacancie"] = True
        return context

    def get_queryset(self):
        return models.Vacancy.objects.select_related("company")


class VacanciesBySpecialty(ListView):
    template_name = "myapp/vacancies.html"
    allow_empty = False

    def get_queryset(self):
        return models.Vacancy.objects.filter(
            specialty__code=self.kwargs["specialty"]
        ).select_related("company")


class Vacancy(View):
    # в post нужно вызвать ошибку если юзер anonim !!!
    # вернуть 404 ошибку если страница не существует (вакансия)
    # Как сделать, чтобы UniqueConstraint возвращало человеческую ошибку? Если выключить debug true, то? Проверить.

    def get(self, request, vacancy_id):
        form = ApplicationForm()
        vacancy = models.Vacancy.objects.get(id=vacancy_id)
        context = {"form": form, "vacancy": vacancy}
        return render(request, "myapp/vacancy.html", context)

    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return HttpResponse(status=403)
        form = ApplicationForm(request.POST)
        # Доп можно сделать, если пользователь уже отправлял отклик, то скрыть для него форму
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.vacancy = models.Vacancy.objects.get(id=self.kwargs["vacancy_id"])
            instance.save()
            return redirect(
                reverse_lazy(
                    "vacancy_send", kwargs={"vacancy_id": self.kwargs["vacancy_id"]}
                )
            )
        return render(request, "sent.html", {"form": form})


class Company(ListView):
    model = models.Vacancy
    template_name = "myapp/company.html"
    pk_url_kwarg = "company_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = get_object_or_404(
            models.Company, id=self.kwargs["company_id"]
        )
        return context

    def get_queryset(self):
        return models.Vacancy.objects.filter(
            company__id=self.kwargs["company_id"]
        ).select_related("company")


# VacancySend
# MyComapanyCreate
# MyCompany
# MyCompanyVacanciesList
# MyComapnyVacanciesCreate
# MyCompanyVacancy

# Сделать кнопку назад на странице с выдачей по вакансиям
# Прикрутить поиск в самом конце (сделать хотя бы часть сложного варианта)

# (!!!) Важно
# Проверку наличия компании можно попробовать реализовать через
# Написать 2 своих миксина на основе PermissionRequiredMixin - что компания есть и что компании нет

# Запретить доступ не к своей компании и ее вакансиям


class MyComapanyStart(LoginRequiredMixin, UserMustHasNotCompany, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        return render(request, "myapp/company-create.html", context={})


class MyCompanyCreate(LoginRequiredMixin, UserMustHasNotCompany, View):
    login_url = "/login/"
    # наполить словарь контекста для шаблона

    def get(self, request):
        form = CompanyForm()
        context = {"form": form}
        return render(request, "myapp/company-edit.html", context)

    def post(self, request):
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.owner = request.user
            instance.save()
            return redirect(reverse_lazy("my_company"))
        context = {"form": form}
        return render(request, "myapp/company-edit.html", context)


class MyCompany(LoginRequiredMixin, UserMustHasCompany, View):
    login_url = "/login/"
    # наполить словарь контекста для шаблона

    def get(self, request):
        company = models.Company.objects.get(owner=request.user)
        form = CompanyForm(instance=company)
        context = {"form": form}
        return render(request, "myapp/company-edit.html", context)

    def post(self, request):
        company = models.Company.objects.get(owner=request.user)
        form = CompanyForm(request.POST, request.FILES, instance=company)
        context = {"form": form}
        if form.is_valid():
            instance = form.save(commit=False)
            instance.owner = request.user
            instance.save()
            context["status"] = "Информация о компании обновлена"
        else:
            context["status"] = "Обновления не сохранены. Исправьте ошибки"
        return render(request, "myapp/company-edit.html", context)


class MyCompanyVacanciesList(LoginRequiredMixin, UserMustHasCompany, View):
    login_url = "/login/"

    # наполить словарь контекста для шаблона
    def get(self, request):
        vacancies = models.Company.objects.get(owner=request.user).vacancies.all()
        context = {"vacancies": vacancies}
        return render(request, "myapp/vacancy-list.html", context)


class VacancySend(View):
    # шаблон доделать
    def get(self, request, vacancy_id):
        return render(request, "myapp/sent.html", {"vacancy_id": vacancy_id})


class MyComapnyVacanciesCreate(LoginRequiredMixin, UserMustHasCompany, View):
    login_url = "/login/"
    # наполить словарь контекста для шаблона

    def get(self, request):
        form = VacancyForm()
        context = {"form": form}
        return render(request, "myapp/vacancy-edit.html", context)

    def post(self, request):
        form = VacancyForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.company = request.user.company
            instance.save()
            return redirect(
                reverse_lazy("my_company_vacancy", kwargs={"vacancy_id": instance.id})
            )
        context = {"form": form, "status": "Исправьте ошибки в форме"}
        return render(request, "myapp/vacancy-edit.html", context)


class MyCompanyVacancy(LoginRequiredMixin, UserViewOnlyYourVacancies, View):
    login_url = "/login/"
    # наполить словарь контекста для шаблона

    def get(self, request, vacancy_id):
        vacancy = get_object_or_404(models.Vacancy, id=vacancy_id)
        form = VacancyForm(instance=vacancy)
        context = {"form": form, "vacancy": vacancy}
        return render(request, "myapp/vacancy-edit.html", context)

    def post(self, request, vacancy_id):
        vacancy = get_object_or_404(models.Vacancy, id=vacancy_id)
        form = VacancyForm(request.POST, instance=vacancy)
        context = {"form": form, "vacancy": vacancy}
        # добавить в контекст отклики на форму
        if form.is_valid():
            instance = form.save(commit=False)
            instance.company = request.user.company
            instance.save()
            context["status"] = "Вакансия обновлена"
        else:
            context["status"] = "Обновления не сохранены. Исправьте ошибки"
        return render(request, "myapp/vacancy-edit.html", context)
