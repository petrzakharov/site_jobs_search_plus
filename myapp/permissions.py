from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from . import models


class UserMustHasNotCompany(UserPassesTestMixin):
    redirect_url = "my_company"

    def test_func(self):
        return not models.Company.objects.filter(owner=self.request.user).exists()

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect(self.redirect_url)


class UserMustHasCompany(UserPassesTestMixin):
    redirect_url = "my_company_start"

    def test_func(self):
        return models.Company.objects.filter(owner=self.request.user).exists()

    def handle_no_permission(self):
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
