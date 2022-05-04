from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, UpdateView
from django.views.generic.base import TemplateView

from . import models
from .forms import ApplicationForm, CompanyForm, SearchForm, VacancyForm
from .permissions import (
    UserMustHasCompany,
    UserMustHasNotCompany,
    UserViewOnlyYourVacancies,
)


class Index(TemplateView):
    template_name = "myapp/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = SearchForm()
        context["specialties"] = models.Specialty.objects.annotate(
            count=Count("vacancies")
        )
        context["companies"] = models.Company.objects.values("logo", "id").annotate(
            count=Count("vacancies")
        )
        context["hints"] = ["Python", "Flask", "Django", "Парсинг", "ML"]
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
    def get(self, request, vacancy_id):
        form = ApplicationForm()
        vacancy = get_object_or_404(models.Vacancy, id=vacancy_id)
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


class VacancySend(View):
    # ВСЕ ОК, кроме не грузящейся зеленой галочки
    """
    Отправка отклика на вакансию
    """

    def get(self, request, vacancy_id):
        back_url = reverse_lazy(
            "vacancy", kwargs={"vacancy_id": self.kwargs["vacancy_id"]}
        )
        return render(
            request,
            "myapp/sent.html",
            {
                "vacancy_id": vacancy_id,
                "back_url": back_url,
            },
        )


class MyCompanyStart(LoginRequiredMixin, UserMustHasNotCompany, View):
    """
    Предложение создать компанию
    """

    # ВСЕ ОК
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        return render(request, "myapp/company-create.html")


class MyCompanyCreate(LoginRequiredMixin, UserMustHasNotCompany, View):
    """
    Создание компании
    """

    login_url = "/login/"
    # ВСЕ ОК, можно переписать на дженерике
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
    """
    Отображени/редактирование существующей компании
    """

    login_url = "/login/"
    # ВСЕ ОК, но можно переписать на дженериках и добавить отображение логотипа
    # Статус обновления не сохранены можно убрать если перепишу на дженериках, форма и так говорит про ошибки
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


# class MyCompany(LoginRequiredMixin, UserMustHasCompany, UpdateView):
#     model = models.Company
#     template_name = "myapp/company-edit.html"
#     form_class = CompanyForm
#     success_url = reverse_lazy("my_company")

#     # не могу сформировать обновление статуса, непонятно как проверить что формы была правильно сохранена

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context

#     def form_valid(self, form, **kwargs):
#         self.object = form.save(commit=False)
#         self.object.owner = self.request.user
#         self.object.save()
#         return super().form_valid(form)

#     def get_object(self):
#         return models.Company.objects.get(owner=self.request.user)


class MyCompanyVacanciesList(LoginRequiredMixin, UserMustHasCompany, View):
    """
    Список сохраненных вакансий владельца компании
    """

    login_url = "/login/"
    # ВСЕ ОК
    def get(self, request):
        company = models.Company.objects.get(owner=request.user)
        vacancies = models.Vacancy.objects.filter(company=company).annotate(
            count_application=Count("applications")
        )
        context = {"vacancies": vacancies}
        return render(request, "myapp/vacancy-list.html", context)


class MyCompanyVacancy(LoginRequiredMixin, UserViewOnlyYourVacancies, View):
    """
    Отображение/редактирование одной вакансии
    """

    login_url = "/login/"
    # ВСЕ ОК, но можно переписать на дженерики

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


class MyComapnyVacanciesCreate(LoginRequiredMixin, UserMustHasCompany, View):
    """
    Создание новой вакансии
    """

    login_url = "/login/"
    # ВСЕ ОК, но можно переписать на дженерики

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


class SearchView(ListView):
    # ВСЕ ОК
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
