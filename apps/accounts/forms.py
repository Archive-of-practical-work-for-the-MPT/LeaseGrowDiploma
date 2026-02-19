from django import forms
from django.core.exceptions import ValidationError

from .models import Account, UserProfile


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=255,
        label='Email или логин',
        widget=forms.TextInput(attrs={
            'autocomplete': 'username',
            'placeholder': 'Введите email или логин',
        }),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'placeholder': 'Введите пароль',
        }),
    )


class RegisterForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'autocomplete': 'email',
            'placeholder': 'example@mail.ru',
        }),
    )
    username = forms.CharField(
        max_length=100,
        label='Логин',
        widget=forms.TextInput(attrs={
            'autocomplete': 'username',
            'placeholder': 'Придумайте логин',
        }),
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'placeholder': 'Не менее 8 символов',
        }),
    )
    password2 = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'placeholder': 'Повторите пароль',
        }),
    )
    first_name = forms.CharField(
        max_length=100,
        label='Имя',
        widget=forms.TextInput(attrs={'placeholder': 'Иван'}),
    )
    last_name = forms.CharField(
        max_length=100,
        label='Фамилия',
        widget=forms.TextInput(attrs={'placeholder': 'Иванов'}),
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label='Телефон',
        widget=forms.TextInput(attrs={'placeholder': '+7 (999) 123-45-67'}),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and Account.objects.filter(username__iexact=username).exists():
            raise ValidationError('Пользователь с таким логином уже существует.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Account.objects.filter(email__iexact=email).exists():
            raise ValidationError('Пользователь с таким email уже зарегистрирован.')
        return email

    def clean(self):
        data = super().clean()
        p1 = data.get('password1')
        p2 = data.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError({'password2': 'Пароли не совпадают.'})
        if p1 and len(p1) < 8:
            raise ValidationError({'password1': 'Пароль должен быть не менее 8 символов.'})
        return data
