from django import forms
from django.core.exceptions import ValidationError

from .models import Account, UserProfile


class ClientCompanyForm(forms.Form):
    """Форма добавления/редактирования компании клиентом (для оформления заявок на лизинг)."""
    name = forms.CharField(
        max_length=255,
        label='Название компании',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ООО «Ромашка»'}),
    )
    inn = forms.CharField(
        max_length=12,
        label='ИНН',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '1234567890'}),
    )
    legal_address = forms.CharField(
        required=False,
        label='Юридический адрес',
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label='Телефон',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+7 (999) 123-45-67'}),
    )
    email = forms.EmailField(
        required=False,
        label='Email компании',
        widget=forms.EmailInput(attrs={'class': 'form-input'}),
    )

    def __init__(self, instance=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance

    def clean_inn(self):
        from apps.leasing.models import Company
        inn = (self.cleaned_data.get('inn') or '').strip()
        if len(inn) < 10:
            raise ValidationError('ИНН должен содержать 10 или 12 цифр.')
        if not inn.isdigit():
            raise ValidationError('ИНН должен содержать только цифры.')
        qs = Company.objects.filter(inn=inn)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Компания с таким ИНН уже зарегистрирована.')
        return inn


class PasswordResetRequestForm(forms.Form):
    """Форма запроса сброса пароля — email или логин."""
    email_or_username = forms.CharField(
        max_length=255,
        label='Email или логин',
        widget=forms.TextInput(attrs={
            'autocomplete': 'username',
            'placeholder': 'Введите email или логин',
        }),
    )


class PasswordResetConfirmForm(forms.Form):
    """Форма установки нового пароля."""
    password1 = forms.CharField(
        label='Новый пароль',
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

    def clean(self):
        data = super().clean()
        p1 = data.get('password1')
        p2 = data.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError({'password2': 'Пароли не совпадают.'})
        if p1 and len(p1) < 8:
            raise ValidationError({'password1': 'Пароль должен быть не менее 8 символов.'})
        return data


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
    privacy_agree = forms.BooleanField(
        required=True,
        label='Согласие с политикой конфиденциальности',
        error_messages={'required': 'Необходимо согласиться с политикой обработки персональных данных.'},
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


class ProfileEditForm(forms.Form):
    """Форма редактирования профиля и аккаунта пользователем."""

    username = forms.CharField(
        max_length=100,
        label='Логин',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Логин для входа',
        }),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'example@mail.ru',
        }),
    )
    first_name = forms.CharField(
        max_length=100,
        label='Имя',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Иван',
        }),
    )
    last_name = forms.CharField(
        max_length=100,
        label='Фамилия',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Иванов',
        }),
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label='Телефон',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+7 (999) 123-45-67',
        }),
    )
    current_password = forms.CharField(
        required=False,
        label='Текущий пароль (для сохранения изменений)',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите пароль для подтверждения',
            'autocomplete': 'current-password',
        }),
    )
    new_password = forms.CharField(
        required=False,
        label='Новый пароль (оставьте пустым, чтобы не менять)',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Не менее 8 символов',
            'autocomplete': 'new-password',
        }),
    )
    new_password_confirm = forms.CharField(
        required=False,
        label='Повторите новый пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Повторите новый пароль',
            'autocomplete': 'new-password',
        }),
    )

    def __init__(self, account=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account = account

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise ValidationError('Логин обязателен.')
        qs = Account.objects.filter(username__iexact=username)
        if self.account:
            qs = qs.exclude(id=self.account.id)
        if qs.exists():
            raise ValidationError('Этот логин уже занят.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise ValidationError('Email обязателен.')
        qs = Account.objects.filter(email__iexact=email)
        if self.account:
            qs = qs.exclude(id=self.account.id)
        if qs.exists():
            raise ValidationError('Этот email уже зарегистрирован.')
        return email

    def clean(self):
        data = super().clean()
        current = data.get('current_password')
        new_pwd = data.get('new_password')
        new_pwd_confirm = data.get('new_password_confirm')

        # Текущий пароль нужен только при смене логина, email или пароля
        needs_password = False
        if self.account:
            needs_password = (
                data.get('username', '').strip() != self.account.username
                or data.get('email', '').strip().lower() != self.account.email
                or bool(new_pwd)
            )
        if self.account and needs_password:
            if not current:
                raise ValidationError({
                    'current_password': 'Введите текущий пароль для подтверждения изменений.',
                })
            from django.contrib.auth.hashers import check_password
            if not check_password(current, self.account.password_hash):
                raise ValidationError({
                    'current_password': 'Неверный текущий пароль.',
                })

        if new_pwd or new_pwd_confirm:
            if new_pwd != new_pwd_confirm:
                raise ValidationError({'new_password_confirm': 'Пароли не совпадают.'})
            if len(new_pwd or '') < 8:
                raise ValidationError({'new_password': 'Пароль должен быть не менее 8 символов.'})

        return data
