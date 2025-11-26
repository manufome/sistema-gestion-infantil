from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=[
        ('teacher', 'Teacher'),
        ('guardian', 'Guardian')
    ], required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password1', 'password2', 'role']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError(
                "Ingrese una dirección de correo electrónico válida.")
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                "Este correo electrónico ya está registrado.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 6:
            raise ValidationError(
                "El nombre de usuario debe tener al menos 6 caracteres.")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name.isalpha():
            raise ValidationError("El nombre solo debe contener letras.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name.isalpha():
            raise ValidationError("El apellido solo debe contener letras.")
        return last_name


class UserLoginForm(AuthenticationForm):
    pass


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'groups']
        labels = {
            'groups': 'Roles',
        }
        widgets = {
            'groups': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['groups'].queryset = Group.objects.exclude(
            name='Administrator')
