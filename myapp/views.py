from calendar import c

from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView

from . import models
from .forms import CompanyForm, VacancyForm


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


class Vacancy(DetailView):
    model = models.Vacancy
    template_name = "myapp/vacancy.html"
    pk_url_kwarg = "vacancy_id"
    context_object_name = "vacancy"

    # тут добавить форму отклика, если пришел post запрос то ...
    # переписать на get / post запросах
    # при post запросе создаем связь в таблице откликов и переадресуем в VacancySend


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


class MyComapanyStart(View):
    # только для залогиненого пользователя
    # у пользователя должна не должно быть компании
    def get(self, request, *args, **kwargs):
        company_qs = models.Company.objects.filter(owner=request.user)
        if company_qs.exists():
            return redirect(reverse_lazy("my_company"))
        return render(request, "company-create.html", context={})


class MyComapanyCreate(View):
    # только для залогиненого пользователя
    # у пользователя должна не должно быть компании
    def get(self, request):
        if models.Company.objects.filter(owner=request.user).exists():
            return redirect(reverse_lazy("my_company"))
        form = CompanyForm()
        context = {"form": form}
        return render(request, "company-edit.html", context)

    def post(self, request):
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.owner = request.user
            instance.save()
            return redirect(reverse_lazy("my_company"))
        # context = {} добавить все необходимое в контекст
        return render(request, "company-edit.html", {"form": form})


class MyCompany(View):
    # только для залогиненого пользователя
    # у пользователя должна быть компания
    def get(self, request):
        # Мне нужен id company
        company_qs = models.Company.objects.filter(owner=request.user)
        if not company_qs.exists():
            return redirect(reverse_lazy("my_company_start"))
        form = CompanyForm(instance=company_qs.first())
        context = {"form": form}
        return render(request, "company-edit.html", context)

    def post(self, request):
        company = models.Company.objects.filter(owner=request.user).first()
        form = CompanyForm(request.POST, request.FILES, instance=company)
        context = {"form": form}
        if form.is_valid():
            instance = form.save(commit=False)
            instance.owner = request.user
            instance.save()
            context["status"] = "Информация о компании обновлена"
        else:
            context["status"] = "Обновления не сохранены. Исправьте ошибки"
        return render(request, "company-edit.html", context)


class MyCompanyVacanciesList(View):
    # только для залогиненого пользователя
    # у пользователя должна быть компания
    def get(self, request):
        company_qs = models.Company.objects.filter(owner=request.user)
        if not company_qs.exists():
            return redirect(reverse_lazy("my_company_start"))
        company = company_qs[0]
        # тут оптимизировать формирование контекста
        context = {"vacancies": company.vacancies.all()}
        return render(request, "vacancy-list.html", context)


class VacancySend(View):
    def get(self, request, vacancy_id):
        return render(request, "sent.html", {"vacancy_id": vacancy_id})


class MyComapnyVacanciesCreate(View):
    # только для залогиненого пользователя
    # у пользователя должна быть компания
    def get(self, request):
        company_qs = models.Company.objects.filter(owner=request.user)
        if not company_qs.exists():
            return redirect(reverse_lazy("my_company_start"))
        form = VacancyForm()
        return render(request, "vacancy-edit.html", {"form": form})

    def post(self, request):
        form = VacancyForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.company = request.user.company
            instance.save()
            return redirect(
                reverse_lazy("my_company_vacancy", kwargs={"vacancy_id": instance.id})
            )
        # context = {"context": context}
        return render(request, "vacancy-edit.html", {"form": form})


class MyCompanyVacancy(View):
    # только для залогиненого пользователя
    # у пользователя должна быть компания
    # пользователь должен отправлять запрос к вакансии своей компании
    def get(self, request, vacancy_id):
        vacancy = get_object_or_404(models.Vacancy, id=vacancy_id)
        if request.user != vacancy.company.owner:
            return HttpResponse(status=403)
        # context = {} тут добавить отклики
        form = VacancyForm(instance=vacancy)
        return render(request, "vacancy-edit.html", {"form": form})

    def post(self, request, vacancy_id):
        vacancy = get_object_or_404(models.Vacancy, id=vacancy_id)
        if request.user != vacancy.company.owner:
            return HttpResponse(status=403)
        form = VacancyForm(request.POST, instance=vacancy)
        context = {"form": form}
        # добавить в контекст отклики на форму
        if form.is_valid():
            instance = form.save(commit=False)
            instance.company = request.user.company
            instance.save()
            context["status"] = "Вакансия обновлена"
        else:
            context["status"] = "Обновления не сохранены. Исправьте ошибки"
        return render(request, "vacancy-edit.html", context)
