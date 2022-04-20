from django.core.validators import MinValueValidator
from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    logo = models.URLField(default='https://place-hold.it/100x60')
    description = models.TextField(max_length=1000)
    employee_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], blank=False
    )


class Specialty(models.Model):
    code = models.CharField(max_length=30)
    title = models.CharField(max_length=100)
    picture = models.URLField(default='https://place-hold.it/100x60')


class Vacancy(models.Model):
    title = models.CharField(max_length=100)
    specialty = models.ForeignKey(
        Specialty, on_delete=models.CASCADE, related_name='vacancies'
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='vacancies'
    )
    skills = models.CharField(max_length=300)
    description = models.TextField(max_length=1000)
    salary_min = models.PositiveIntegerField(blank=False)
    salary_max = models.PositiveIntegerField(blank=False)
    published_at = models.DateTimeField(auto_now_add=True)
