from re import S
from secrets import choice

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from django.forms import IntegerField
from phone_field import PhoneField

User = get_user_model()


class Company(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="logos/", blank=False)
    description = models.TextField(max_length=1000)
    employee_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], blank=False
    )
    owner = models.OneToOneField(User, related_name="company", on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        self.logo.storage.delete(self.avatar.path)
        super(Company, self).delete(*args, **kwargs)

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"

    def __str__(self):
        return self.name


class Specialty(models.Model):
    code = models.CharField(max_length=30)
    title = models.CharField(max_length=100)
    picture = models.ImageField(upload_to="specialties/", blank=False)

    def delete(self, *args, **kwargs):
        self.picture.storage.delete(self.avatar.path)
        super(Specialty, self).delete(*args, **kwargs)

    class Meta:
        verbose_name = "Специальность"
        verbose_name_plural = "Специальности"

    def __str__(self):
        return self.code

    # Проверить что метод delete отрабатывает, при удалении экземпляра удаляется изображение


class Vacancy(models.Model):
    title = models.CharField(max_length=100)
    specialty = models.ForeignKey(
        Specialty, on_delete=models.CASCADE, related_name="vacancies"
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="vacancies"
    )
    skills = models.CharField(max_length=300)
    description = models.TextField(max_length=1000)
    salary_min = models.PositiveIntegerField(blank=False)
    salary_max = models.PositiveIntegerField(blank=False)
    published_at = models.DateField(auto_now_add=True)

    def clean(self):
        if self.salary_min > self.salary_max:
            raise ValidationError("Ошибка в границах зарплатной вилки")

    class Meta:
        ordering = ("-published_at",)
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"

    def __str__(self):
        return self.title


class Application(models.Model):
    written_username = models.CharField(
        max_length=30, help_text="Ваш юзернейм", blank=False
    )
    written_phone = PhoneField(blank=False, help_text="Номер телефона")
    written_cover_letter = models.TextField(blank=False, max_length=1000)
    vacancy = models.ForeignKey(
        Vacancy, on_delete=models.CASCADE, related_name="applications"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="applications"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "vacancy"], name="user_application"
            ),
        ]

        verbose_name = "Отклик"
        verbose_name_plural = "Отклики"

    def __str__(self):
        return str(self.user.username) + "__" + str(self.vacancy)


class Resume(models.Model):
    class EducationChoices(models.TextChoices):
        missing = "Отсутствует"
        secondary = "Среднее"
        vocational = "Средне-специальное"
        incomplete_higher = "Неполное высшее"
        higher = "Высшее"

    class GradeChoices(models.TextChoices):
        intern = "intern"
        junior = "junior"
        middle = "middle"
        senior = "senior"
        lead = "lead"

    class WorkStatusChoices(models.TextChoices):
        not_in_search = "Не ищу работу"
        consideration = "Рассматриваю предложения"
        in_search = "Ищу работу"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="resumes")
    name = models.CharField(
        max_length=30, validators=[MinLengthValidator(2)], blank=False
    )
    surname = models.CharField(
        max_length=30, validators=[MinLengthValidator(2)], blank=False
    )
    status = models.CharField(choices=WorkStatusChoices.choices, max_length=25)
    salary = models.PositiveIntegerField(blank=False)
    specialty = models.ForeignKey(
        Specialty, on_delete=models.CASCADE, related_name="resumes"
    )
    grade = models.CharField(choices=GradeChoices.choices, max_length=25)
    education = models.CharField(choices=EducationChoices.choices, max_length=25)
    experience = models.PositiveBigIntegerField(blank=False)
    portfolio = models.URLField(blank=True)

    class Meta:
        verbose_name = "Резюме"
        verbose_name_plural = "Резюме"

    def __str__(self):
        return self.name + "__" + str(self.specialty)


# Пицца (у одной пиццы может быть много топпингов)
# Топпинг (один топпинг может быть на многих пиццах)

# Вакансия (у вакансии может быть одна компания)
# Компания (у компании может быть много вакансий)

# Оклик резюме (у отклика может быть только одна вакансия)
# Вакансия (у ваканчии может быть много откликов)

# Отклик резюме (у отклика может быть только один пользователь)
# Юзер (у юзера может быть много откликов)
