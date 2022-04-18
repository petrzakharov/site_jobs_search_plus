from django.core.validators import MinValueValidator
from django.db import models
from django.forms import ChoiceField, DateTimeField, URLField


class Company(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    logo = models.URLField(default='https://place-hold.it/100x60')
    description = models.TextField(max_length=1000)
    employee_count = models.IntegerField(
        validators=[MinValueValidator(1)], blank=False
    )


class Specialty(models.Model):
    code = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    picture = models.URLField(default='https://place-hold.it/100x60')


class Vacancy(models.Model):
    title = models.CharField(max_length=200)
    specialty = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='vacancies'
    )
    skills = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    salary_min = models.FloatField(
        validators=[MinValueValidator(1.0)], blank=False
    )
    salary_max = models.FloatField()
    published_at = DateTimeField()
