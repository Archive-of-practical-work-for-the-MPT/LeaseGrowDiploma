"""Формы для приложения лизинга."""
from calendar import monthrange
from datetime import date, datetime

from django import forms
from django.db.models import Q
from .models import LeaseContract
from apps.leasing.models import Company


def _add_months(d, months):
    """Добавить месяцы к дате."""
    m = d.month - 1 + months
    y = d.year + m // 12
    m = m % 12 + 1
    last_day = monthrange(y, m)[1]
    day = min(d.day, last_day)
    return date(y, m, day)


def _next_contract_number():
    """Генерация номера договора LG-YYYY-NNN."""
    from django.db.models import Max
    year = date.today().year
    prefix = f'LG-{year}-'
    last = LeaseContract.objects.filter(
        contract_number__startswith=prefix
    ).aggregate(m=Max('contract_number'))['m']
    if last:
        try:
            n = int(last.split('-')[-1]) + 1
        except (ValueError, IndexError):
            n = 1
    else:
        n = 1
    return f'{prefix}{n:03d}'


class ContractFromRequestForm(forms.ModelForm):
    """Форма создания договора из подтверждённой заявки. Техника и клиент заданы заявкой."""

    class Meta:
        model = LeaseContract
        fields = [
            'contract_number', 'company',
            'start_date', 'end_date', 'lease_term_months',
            'total_amount', 'advance_payment', 'monthly_payment', 'payment_day',
            'status',
        ]
        labels = {
            'contract_number': 'Номер договора',
            'company': 'Компания (арендатор)',
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
            'lease_term_months': 'Срок (мес.)',
            'total_amount': 'Общая сумма (руб.)',
            'advance_payment': 'Авансовый платёж (руб.)',
            'monthly_payment': 'Ежемесячный платёж (руб.)',
            'payment_day': 'День платежа (1–31)',
            'status': 'Статус',
        }
        widgets = {
            'contract_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'LG-2026-001'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-input form-input-auto', 'type': 'date', 'readonly': True}),
            'lease_term_months': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-input form-input-auto', 'readonly': True}),
            'advance_payment': forms.NumberInput(attrs={'class': 'form-input'}),
            'monthly_payment': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'step': 0.01}),
            'payment_day': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 31}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, client_account=None, lease_request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._lease_request = lease_request
        eq = lease_request.equipment if lease_request else None
        account = lease_request.account if lease_request else client_account

        if account:
            companies_qs = Company.objects.filter(status='active').filter(
                Q(account=account) | Q(account__isnull=True)
            ).order_by('name')
            self.fields['company'].queryset = companies_qs
            # Авто-подстановка компании клиента
            client_company = Company.objects.filter(account=account).first()
            if client_company and not self.initial.get('company'):
                self.initial['company'] = client_company

        if not self.initial.get('contract_number'):
            self.initial['contract_number'] = _next_contract_number()

        today = date.today()
        if not self.initial.get('start_date'):
            self.initial['start_date'] = today

        # Начальные значения из техники
        months = 12
        monthly = None
        if eq:
            monthly = eq.monthly_lease_rate
            if not monthly and eq.price:
                monthly = eq.price / 100  # минимальный платёж ~1% от стоимости
        if monthly:
            self.initial['monthly_payment'] = monthly
        self.initial['lease_term_months'] = months

        total = (monthly or 0) * months
        if total:
            self.initial['total_amount'] = total
        if self.initial.get('start_date') and months:
            start = self.initial['start_date']
            if isinstance(start, str):
                start = datetime.strptime(start, '%Y-%m-%d').date()
            self.initial['end_date'] = _add_months(start, months)

        self.fields['advance_payment'].required = False

    def clean(self):
        data = super().clean()
        monthly = data.get('monthly_payment')
        months = data.get('lease_term_months')
        start = data.get('start_date')
        advance = data.get('advance_payment') or 0

        # Ежемесячный платёж не меньше указанного у техники
        if monthly is not None and self._lease_request:
            eq = self._lease_request.equipment
            min_monthly = eq.monthly_lease_rate if eq and eq.monthly_lease_rate else None
            if min_monthly is not None and monthly < min_monthly:
                from django.core.exceptions import ValidationError
                self.add_error('monthly_payment', f'Не менее {float(min_monthly):,.0f} ₽/мес (указано для техники)')

        if monthly is not None and months:
            data['total_amount'] = advance + monthly * months
        if start and months:
            data['end_date'] = _add_months(start, months)
        return data
