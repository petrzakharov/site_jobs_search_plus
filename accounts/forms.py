from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Field, Layout, Row, Submit
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "password1")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields["password2"]

        for fieldname in ["username", "first_name", "last_name", "password1"]:
            self.fields[fieldname].help_text = None
        self.fields["username"].label = "Логин"
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "username",
            "first_name",
            "last_name",
            "password1",
            Submit(
                "submit",
                "Зарегистрироваться",
                css_class="btn btn-primary btn-lg btn-block",
            ),
        )


class AuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Логин"
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("username", css_class="mt-5 form-label-group"),
            ),
            Row(
                Column("password", css_class="form-label-group"),
            ),
            Submit(
                "submit",
                "Войти",
                css_class="btn btn-primary btn-lg btn-block",
            ),
        )
