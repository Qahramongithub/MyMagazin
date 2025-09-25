from django import forms
from django.contrib.auth.forms import UserCreationForm, ReadOnlyPasswordHashField
from .models import User  # yoki CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)


class CustomUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label=("password"),
        help_text=("You can change the password using <a href=\"../password/\">this form</a>.")
    )

    class Meta:
        model = User
        fields = ("username", "password", "is_active", "is_staff")
