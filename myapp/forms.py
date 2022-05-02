from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms
from django.urls import reverse

from . import models


class CompanyForm(forms.ModelForm):
    logo = forms.ImageField(
        widget=forms.FileInput,
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("name"),
                Column("location"),
            ),
            Row(
                Column("employee_count"),
            ),
            FieldWithButtons(
                "logo",
                StrictButton("Загрузить", type="submit", css_class="btn btn-info px-4"),
            ),
            "description",
            Submit("submit", "Сохранить", css_class="btn btn-info"),
        )


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(Column("title"), Column("specialty")),
            Row(Column("salary_min"), Column("salary_max")),
            "skills",
            "description",
            Submit(
                "submit",
                "Сохранить",
                css_class="btn btn-info",
            ),
        )


class ApplicationForm(forms.ModelForm):
    written_phone = forms.RegexField(
        regex=r"^\+?1?\d{9,15}$",
        help_text="Ваш номер в формате +7XXXXXXXXXX",
        label="Ваш номер",
    )

    class Meta:
        model = models.Application
        fields = (
            "written_username",
            "written_phone",
            "written_cover_letter",
        )
        labels = {
            "written_username": "Вас зовут",
            "written_phone": "Ваш телефон",
            "written_cover_letter": "Сопроводительное письмо",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(Column("written_username", css_class="mb-1 mt-2")),
            Row(Column("written_phone", css_class="mb-1")),
            Row(Column("written_cover_letter", css_class="mb-1")),
            Submit("submit", "Отправить", css_class="btn btn-primary mt-4 mb-2"),
        )


class SearchForm(forms.Form):
    search = forms.CharField(required=False, label="")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "get"
        self.helper.form_action = reverse("search")
        self.helper.layout = Layout(
            Row("search", css_clss="form-control w-100"),
            Submit("submit", "Найти", css_class="btn btn-primary w-100"),
        )
