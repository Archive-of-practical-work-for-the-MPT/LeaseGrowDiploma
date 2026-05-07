"""Формы для панели управления."""
import json
import secrets
from pathlib import Path
from uuid import uuid4
from django import forms
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.utils.text import slugify

from apps.accounts.models import Role, Account, UserProfile, AccountToken
from apps.catalog.models import EquipmentCategory, Manufacturer, Equipment
from apps.leasing.models import (
    Company, LeaseContract, LeaseRequest, PaymentSchedule,
    MaintenanceRequest,
)


class RoleForm(forms.ModelForm):
    permissions = forms.CharField(
        required=False,
        label='Права доступа',
        widget=forms.Textarea(attrs={
            'class': 'form-input', 'rows': 2,
            'placeholder': '["all"] или ["contracts","companies"]',
        }),
    )

    class Meta:
        model = Role
        fields = ['name', 'permissions']
        labels = {
            'name': 'Название',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.permissions:
            self.initial['permissions'] = json.dumps(
                self.instance.permissions, ensure_ascii=False
            )

    def clean_permissions(self):
        val = self.cleaned_data.get('permissions')
        if isinstance(val, str) and val.strip():
            try:
                return json.loads(val)
            except json.JSONDecodeError:
                raise forms.ValidationError('Некорректный JSON')
        return []


class AccountForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        label='Пароль (оставьте пустым, чтобы не менять)',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input', 'autocomplete': 'new-password'
        }),
    )

    class Meta:
        model = Account
        fields = ['email', 'username', 'role', 'is_active']
        labels = {
            'email': 'Email',
            'username': 'Логин',
            'role': 'Роль',
            'is_active': 'Активен',
        }
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['password'].required = True
            self.fields['password'].label = 'Пароль'

    def save(self, commit=True):
        obj = super().save(commit=False)
        pwd = self.cleaned_data.get('password')
        if pwd:
            obj.password_hash = make_password(pwd)
        if commit:
            obj.save()
        return obj


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'account', 'first_name', 'last_name', 'phone',
            'passport_series', 'passport_number',
        ]
        labels = {
            'account': 'Аккаунт',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'phone': 'Телефон',
            'passport_series': 'Серия паспорта',
            'passport_number': 'Номер паспорта',
        }
        widgets = {
            'account': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'passport_series': forms.TextInput(attrs={'class': 'form-input', 'maxlength': '4'}),
            'passport_number': forms.TextInput(attrs={'class': 'form-input', 'maxlength': '6'}),
        }


class AccountTokenForm(forms.ModelForm):
    class Meta:
        model = AccountToken
        fields = ['account']
        labels = {'account': 'Аккаунт'}
        widgets = {'account': forms.Select(attrs={'class': 'form-select'})}

    def save(self, commit=True):
        obj = super().save(commit=False)
        if not obj.key:
            obj.key = secrets.token_hex(32)
        if commit:
            obj.save()
        return obj


class EquipmentCategoryForm(forms.ModelForm):
    class Meta:
        model = EquipmentCategory
        fields = ['name', 'parent']
        labels = {
            'name': 'Название',
            'parent': 'Родительская категория',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
        }


class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = ['name', 'country']
        labels = {
            'name': 'Название',
            'country': 'Страна',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'country': forms.TextInput(attrs={'class': 'form-input'}),
        }


class EquipmentForm(forms.ModelForm):
    image_file = forms.FileField(
        required=False,
        label='Загрузить изображение',
        help_text='Форматы: JPEG, PNG, WEBP. Файл сохраняется в каталог медиа и сразу доступен по URL без collectstatic.',
        widget=forms.ClearableFileInput(attrs={'class': 'form-input', 'accept': '.jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp'}),
    )

    class Meta:
        model = Equipment
        fields = [
            'name', 'model', 'category', 'manufacturer', 'specifications',
            'year', 'vin', 'condition', 'status', 'price', 'residual_value',
            'monthly_lease_rate', 'location', 'images_urls',
        ]
        labels = {
            'name': 'Название',
            'model': 'Модель',
            'category': 'Категория',
            'manufacturer': 'Производитель',
            'specifications': 'Характеристики',
            'year': 'Год выпуска',
            'vin': 'VIN',
            'condition': 'Состояние',
            'status': 'Статус',
            'price': 'Цена',
            'residual_value': 'Остаточная стоимость',
            'monthly_lease_rate': 'Платёж в месяц',
            'location': 'Местоположение',
            'images_urls': 'URL изображений',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'model': forms.TextInput(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'manufacturer': forms.Select(attrs={'class': 'form-select'}),
            'specifications': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 3,
                'placeholder': 'Мощность 370 л.с., дизель, масса 8000 кг',
            }),
            'year': forms.NumberInput(attrs={'class': 'form-input'}),
            'vin': forms.TextInput(attrs={'class': 'form-input'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-input'}),
            'residual_value': forms.NumberInput(attrs={'class': 'form-input'}),
            'monthly_lease_rate': forms.NumberInput(attrs={'class': 'form-input'}),
            'location': forms.TextInput(attrs={'class': 'form-input'}),
            'images_urls': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 2,
                'placeholder': 'https://example.com/image.jpg',
            }),
        }

    def clean_images_urls(self):
        """Храним в JSONField список URL — шаблоны и фильтры ожидают один URL через first_image_url."""
        val = self.cleaned_data.get('images_urls')
        if val is None:
            return []
        if isinstance(val, (list, tuple)):
            cleaned = []
            for x in val:
                if x is None:
                    continue
                s = str(x).strip()
                if s:
                    cleaned.append(s)
            return cleaned
        if isinstance(val, str):
            text = val.strip()
            if not text:
                return []
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return [
                        str(x).strip()
                        for x in parsed
                        if str(x).strip()
                    ]
                if isinstance(parsed, str):
                    s = parsed.strip()
                    return [s] if s else []
            except json.JSONDecodeError:
                pass
            return [text]

        return []

    def clean_image_file(self):
        uploaded = self.cleaned_data.get('image_file')
        if not uploaded:
            return uploaded
        ext = Path(uploaded.name).suffix.lower()
        allowed = {'.jpg', '.jpeg', '.png', '.webp'}
        if ext not in allowed:
            raise forms.ValidationError('Разрешены только файлы JPEG, PNG или WEBP.')
        return uploaded

    def save(self, commit=True):
        obj = super().save(commit=False)
        uploaded = self.cleaned_data.get('image_file')
        if uploaded:
            media_dir = Path(settings.MEDIA_ROOT) / 'leasing' / 'products'
            media_dir.mkdir(parents=True, exist_ok=True)
            ext = Path(uploaded.name).suffix.lower()
            safe_base = slugify(f'{obj.name}-{obj.model}') or 'equipment'
            filename = f'{safe_base}-{uuid4().hex[:8]}{ext}'
            target_path = media_dir / filename
            with target_path.open('wb+') as destination:
                for chunk in uploaded.chunks():
                    destination.write(chunk)
            base = (settings.MEDIA_URL or '/media/').rstrip('/')
            obj.images_urls = [f'{base}/leasing/products/{filename}']
        if commit:
            obj.save()
        return obj


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'name', 'inn',
            'address', 'phone', 'email',
            'status', 'account',
        ]
        labels = {
            'name': 'Название',
            'inn': 'ИНН',
            'address': 'Адрес',
            'phone': 'Телефон',
            'email': 'Email',
            'status': 'Статус',
            'account': 'Аккаунт',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'inn': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'account': forms.Select(attrs={'class': 'form-select'}),
        }


class LeaseRequestForm(forms.ModelForm):
    class Meta:
        model = LeaseRequest
        fields = [
            'equipment', 'account', 'status', 'message',
            'manager_notes', 'confirmed_by',
        ]
        labels = {
            'equipment': 'Техника',
            'account': 'Пользователь',
            'status': 'Статус',
            'message': 'Сообщение',
            'manager_notes': 'Заметки менеджера',
            'confirmed_by': 'Подтвердил',
        }
        widgets = {
            'equipment': forms.Select(attrs={'class': 'form-select'}),
            'account': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'manager_notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
            'confirmed_by': forms.Select(attrs={'class': 'form-select'}),
        }


class LeaseContractForm(forms.ModelForm):
    class Meta:
        model = LeaseContract
        fields = [
            'contract_number', 'company', 'equipment',
            'start_date', 'end_date', 'lease_term_months',
            'total_amount', 'advance_payment', 'monthly_payment', 'payment_day',
            'status', 'signed_at', 'signed_by', 'created_by',
        ]
        labels = {
            'contract_number': 'Номер договора',
            'company': 'Компания',
            'equipment': 'Техника',
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
            'lease_term_months': 'Срок (мес.)',
            'total_amount': 'Общая сумма',
            'advance_payment': 'Авансовый платёж',
            'monthly_payment': 'Ежемесячный платёж',
            'payment_day': 'День платежа',
            'status': 'Статус',
            'signed_at': 'Дата подписания',
            'signed_by': 'Подписант',
            'created_by': 'Создал',
        }
        widgets = {
            'contract_number': forms.TextInput(attrs={'class': 'form-input'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'equipment': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={
                'class': 'form-input', 'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-input', 'type': 'date'
            }),
            'lease_term_months': forms.NumberInput(attrs={'class': 'form-input'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-input'}),
            'advance_payment': forms.NumberInput(attrs={'class': 'form-input'}),
            'monthly_payment': forms.NumberInput(attrs={'class': 'form-input'}),
            'payment_day': forms.NumberInput(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'signed_at': forms.DateTimeInput(attrs={
                'class': 'form-input', 'type': 'datetime-local',
            }),
            'signed_by': forms.Select(attrs={'class': 'form-select'}),
            'created_by': forms.Select(attrs={'class': 'form-select'}),
        }


class PaymentScheduleForm(forms.ModelForm):
    class Meta:
        model = PaymentSchedule
        fields = [
            'contract', 'payment_number', 'due_date', 'amount',
            'status', 'paid_at', 'penalty_amount',
        ]
        labels = {
            'contract': 'Договор',
            'payment_number': 'Номер платежа',
            'due_date': 'Срок оплаты',
            'amount': 'Сумма',
            'status': 'Статус',
            'paid_at': 'Дата оплаты',
            'penalty_amount': 'Штраф',
        }
        widgets = {
            'contract': forms.Select(attrs={'class': 'form-select'}),
            'payment_number': forms.NumberInput(attrs={'class': 'form-input'}),
            'due_date': forms.DateInput(attrs={
                'class': 'form-input', 'type': 'date'
            }),
            'amount': forms.NumberInput(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'paid_at': forms.DateTimeInput(attrs={
                'class': 'form-input', 'type': 'datetime-local',
            }),
            'penalty_amount': forms.NumberInput(attrs={'class': 'form-input'}),
        }


class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = [
            'equipment', 'company', 'description', 'urgency',
            'status', 'assigned_to', 'completed_at',
        ]
        labels = {
            'equipment': 'Техника',
            'company': 'Компания',
            'description': 'Описание',
            'urgency': 'Срочность',
            'status': 'Статус',
            'assigned_to': 'Исполнитель',
            'completed_at': 'Дата завершения',
        }
        widgets = {
            'equipment': forms.Select(attrs={'class': 'form-select'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'urgency': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'completed_at': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'class': 'form-input', 'type': 'datetime-local'},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['completed_at'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']

    def clean(self):
        from django.utils import timezone
        data = super().clean()
        if data.get('status') == 'completed' and not data.get('completed_at'):
            data['completed_at'] = timezone.now()
        return data
