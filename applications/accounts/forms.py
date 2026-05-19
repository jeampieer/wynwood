from django import forms
from django.contrib.auth.forms import UserCreationForm

from applications.accounts.models import User


class GuestRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre completo", max_length=150)
    phone = forms.CharField(label="Teléfono", max_length=30, required=False)
    nationality = forms.CharField(label="Nacionalidad", max_length=80, required=False)

    class Meta:
        model = User
        fields = ("email", "first_name", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
