from audioop import reverse

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import AuthForm, CreationForm


class Register(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("login")
    template_name = "register.html"


class Login(LoginView):
    form_class = AuthForm
    redirect_authenticated_user = True
    template_name = "login.html"


class Logout(LogoutView):
    pass
