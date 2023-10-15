from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import *
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError

# Форма регистрации нового пользователя
class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))  # поле ввода логина
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))  # поле ввода электронной почты
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))  # поле ввода пароля
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))  # поле повторного ввода пароля

    class Meta:
        model = User  # модель пользователя
        fields = ('username', 'email', 'password1', 'password2')  # перечисление полей формы


# Форма входа в систему
class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))  # поле ввода логина
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))  # поле ввода пароля


# Форма создания голосования
class VoteCreateForm(forms.Form):
    title = forms.CharField(label='Название голосования', widget=forms.TextInput(attrs={'class': 'form-input'}))  # поле ввода названия нового голосования


# Форма создания варианта ответа
class ChoiceForm(forms.Form):
    title = forms.CharField(label=mark_safe('<br />Вариант ответа:'), widget=forms.TextInput(attrs={'class': 'form-input'}))  # поле ввода текста нового варианта ответа