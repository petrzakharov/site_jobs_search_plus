from django import forms

from . import models


class CompanyForm(forms.ModelForm):
    class Meta:
        model = models.Company
        fields = (
            "name",
            "location",
            "logo",
            "description",
            "employee_count",
        )
        labels = {
            "name": "Название компании",
            "location": "География",
            "logo": "Логотип",
            "description": "Информация о компании",
            "employee_count": "Количество человек в компании",
        }


class VacancyForm(forms.ModelForm):
    class Meta:
        model = models.Vacancy
        fields = (
            "title",
            "specialty",
            "salary_min",
            "salary_max",
            "skills",
            "description",
        )
        labels = {
            "title": "Название вакансии",
            "specialty": "Специализация",
            "salary_min": "Зарплата от",
            "salary_max": "Зарплата до",
            "skills": "Требуемые навыки",
            "description": "Описание вакансии",
        }
