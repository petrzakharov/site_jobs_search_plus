from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView
from django.views.generic.base import TemplateView

from . import models
from .forms import ApplicationForm, CompanyForm, ResumeForm, VacancyForm
from .permissions import (UserMustHasCompany, UserMustHasNotCompany,
                          UserMustHasNotResume, UserMustHasResume,
                          UserViewOnlyYourVacancies)


class Index(TemplateView):
    """
    Главная страница
    """

    template_name = "myapp/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["specialties"] = models.Specialty.objects.annotate(
            count=Count("vacancies")
        )
        context["companies"] = models.Company.objects.values("logo", "id").annotate(
            count=Count("vacancies")
        )
        context["hints"] = ["Python", "Flask", "Django", "Парсинг", "ML"]
        return context


class VacanciesList(ListView):
    """
    Список всех вакансий
    """

    model = models.Vacancy
    template_name = "myapp/vacancies.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_vacancie"] = True
        return context

    def get_queryset(self):
        return models.Vacancy.objects.select_related("company")


class VacanciesBySpecialty(ListView):
    """
    Список вакансий по специальностям
    """

    template_name = "myapp/vacancies.html"
    allow_empty = False

    def get_queryset(self):
        return models.Vacancy.objects.filter(
            specialty__code=self.kwargs["specialty"]
        ).select_related("company")


class Vacancy(View):
    """
    Отображение вакансии и формы отклика
    """

    def get(self, request, vacancy_id):
        form = ApplicationForm()
        vacancy = get_object_or_404(models.Vacancy, id=vacancy_id)
        user_has_application = False
        if not request.user.is_anonymous:
            user_has_application = models.Application.objects.filter(
                user=self.request.user, vacancy=vacancy
            ).exists()
        context = {
            "form": form,
            "vacancy": vacancy,
            "user_has_application": user_has_application,
        }
        return render(request, "myapp/vacancy.html", context)

    def post(self, request, vacancy_id):
        vacancy = get_object_or_404(models.Vacancy, id=vacancy_id)
        if request.user.is_anonymous:
            return HttpResponse(status=403)
        form = ApplicationForm(request.POST)
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
        return render(request, "myapp/vacancy.html", {"form": form, "vacancy": vacancy})


class Company(ListView):
    """
    Информация о компании
    """

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


class VacancySend(LoginRequiredMixin, TemplateView):
    """
    Страница успешной отправки отклика
    """

    template_name = "myapp/sent.html"
    login_url = "/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vacancy_id = self.kwargs["vacancy_id"]
        back_url = reverse_lazy("vacancy", kwargs={"vacancy_id": vacancy_id})
        context = {"vacancy_id": vacancy_id, "back_url": back_url}
        return context


class MyCompanyStart(LoginRequiredMixin, UserMustHasNotCompany, TemplateView):
    """
    Предложение создать компанию/переадресация на существующую
    """

    login_url = "/login/"
    template_name = "myapp/company-create.html"


class MyCompanyCreate(LoginRequiredMixin, UserMustHasNotCompany, View):
    """
    Создание компании, view
    """

    login_url = "/login/"

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


class MyCompany(
    LoginRequiredMixin, UserMustHasCompany, SuccessMessageMixin, UpdateView
):
    """
    Редакирование данных о компании, generic
    """

    model = models.Company
    template_name = "myapp/company-edit.html"
    form_class = CompanyForm
    success_url = reverse_lazy("my_company")
    success_message = "Изменения успешно сохранены"

    def get_object(self):
        return models.Company.objects.get(owner=self.request.user)


class MyCompanyVacanciesList(LoginRequiredMixin, UserMustHasCompany, TemplateView):
    """
    Список сохраненных вакансий владельца компании
    """

    login_url = "/login/"
    template_name = "myapp/vacancy-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = models.Company.objects.get(owner=self.request.user)
        vacancies = models.Vacancy.objects.filter(company=company).annotate(
            count_application=Count("applications")
        )
        context = {"vacancies": vacancies}
        return context


class MyCompanyVacancy(LoginRequiredMixin, UserViewOnlyYourVacancies, View):
    """
    Отображение/редактирование одной вакансии
    """

    login_url = "/login/"

    def get(self, request, vacancy_id):
        vacancy = get_object_or_404(models.Vacancy, id=vacancy_id)
        applications = models.Application.objects.filter(vacancy=vacancy).all()
        form = VacancyForm(instance=vacancy)
        context = {"form": form, "vacancy": vacancy, "applications": applications}
        return render(request, "myapp/vacancy-edit.html", context)

    def post(self, request, vacancy_id):
        vacancy = get_object_or_404(models.Vacancy, id=vacancy_id)
        form = VacancyForm(request.POST, instance=vacancy)
        context = {"form": form, "vacancy": vacancy}
        if form.is_valid():
            instance = form.save(commit=False)
            instance.company = request.user.company
            instance.save()
            context["status"] = "Вакансия обновлена"
        else:
            context["status"] = "Обновления не сохранены. Исправьте ошибки"
        return render(request, "myapp/vacancy-edit.html", context)


class MyCompanyVacanciesCreate(LoginRequiredMixin, UserMustHasCompany, CreateView):
    """
    Создание вакансии
    """

    template_name = "myapp/vacancy-edit.html"
    form_class = VacancyForm

    def form_valid(self, form, **kwargs):
        self.object = form.save(commit=False)
        self.object.company = self.request.user.company
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("my_company_vacancy", kwargs={"vacancy_id": self.object.id})


class SearchView(ListView):
    """
    Поиск на главной странице
    """

    model = models.Vacancy
    template_name = "myapp/vacancies.html"
    allow_empty = True

    def get_queryset(self):
        query = self.request.GET.get("search")
        if query:
            q = (
                Q(title__icontains=query)
                | Q(skills__icontains=query)
                | Q(company__name__icontains=query)
                | Q(specialty__title__icontains=query)
            )
            return models.Vacancy.objects.filter(q)
        return models.Vacancy.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status"] = "Результаты поиска"
        return context


class LetsCreateResume(LoginRequiredMixin, UserMustHasNotResume, TemplateView):
    login_url = "/login/"
    template_name = "myapp/resume-create.html"


class MyResumeCreate(LoginRequiredMixin, UserMustHasNotResume, CreateView):
    login_url = "/login/"
    template_name = "myapp/resume-edit.html"
    form_class = ResumeForm

    def form_valid(self, form, **kwargs):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("my_resume")


class MyResume(LoginRequiredMixin, UserMustHasResume, SuccessMessageMixin, UpdateView):
    login_url = "/login/"
    template_name = "myapp/resume-edit.html"
    form_class = ResumeForm
    success_url = reverse_lazy("my_resume")
    success_message = "Ваше резюме обновлено!"

    def get_object(self):
        return models.Resume.objects.get(user=self.request.user)
