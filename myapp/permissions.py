from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from . import models


class UserMustHasNotCompany(UserPassesTestMixin):
    redirect_url = "my_company"

    def is_anonym(self):
        return self.request.user.is_anonymous

    def test_func(self):
        return not models.Company.objects.filter(owner=self.request.user).exists()

    def handle_no_permission(self):
        if self.is_anonym():
            return redirect("login")
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect(self.redirect_url)


class UserMustHasCompany(UserPassesTestMixin):
    redirect_url = "my_company_start"

    def is_anonym(self):
        return self.request.user.is_anonymous

    def test_func(self):
        return models.Company.objects.filter(owner=self.request.user).exists()

    def handle_no_permission(self):
        if self.is_anonym():
            return redirect("login")
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect(self.redirect_url)


class UserViewOnlyYourVacancies(UserPassesTestMixin):
    def test_func(self, *args, **kwargs):
        try:
            vacancy = models.Vacancy.objects.get(id=self.kwargs["vacancy_id"])
            return self.request.user == vacancy.company.owner
        except models.Vacancy.DoesNotExist:
            return False


class SuccessMessageMixin:

    success_message = ""

    def form_valid(self, form):
        response = super().form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data


class UserMustHasResume(UserPassesTestMixin):
    redirect_url = "lets_create_resume"

    def is_anonym(self):
        return self.request.user.is_anonymous

    def test_func(self):
        return models.Resume.objects.filter(user=self.request.user).exists()

    def handle_no_permission(self):
        if self.is_anonym():
            return redirect("login")
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect(self.redirect_url)


class UserMustHasNotResume(UserPassesTestMixin):
    redirect_url = "my_resume"

    def is_anonym(self):
        return self.request.user.is_anonymous

    def test_func(self):
        return not models.Resume.objects.filter(user=self.request.user).exists()

    def handle_no_permission(self):
        if self.is_anonym():
            return redirect("login")
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect(self.redirect_url)
