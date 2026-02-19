from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages

from .models import Account, UserProfile, Role
from .forms import LoginForm, RegisterForm


def get_current_account(request):
    """Возвращает аккаунт из сессии или None."""
    account_id = request.session.get('account_id')
    if not account_id:
        return None
    return Account.objects.filter(id=account_id, is_active=True).select_related('role').first()


def login_view(request):
    if get_current_account(request):
        return redirect('core:home')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username'].strip()
        password = form.cleaned_data['password']
        account = Account.objects.filter(
            Q(email__iexact=username) | Q(username__iexact=username),
            is_active=True,
        ).first()
        if account and check_password(password, account.password_hash):
            request.session['account_id'] = account.id
            account.last_login = timezone.now()
            account.save(update_fields=['last_login'])
            messages.success(request, f'Добро пожаловать, {account.username}!')
            return redirect('core:home')
        form.add_error(None, 'Неверный email/логин или пароль.')
    return render(request, 'accounts/auth/login.html', {'form': form})


def register_view(request):
    if get_current_account(request):
        return redirect('core:home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        role_client, _ = Role.objects.get_or_create(
            name='client',
            defaults={'description': 'Клиент (арендатор)'},
        )
        account = Account.objects.create(
            email=form.cleaned_data['email'].strip().lower(),
            username=form.cleaned_data['username'].strip(),
            password_hash=make_password(form.cleaned_data['password1']),
            role=role_client,
            is_active=True,
        )
        UserProfile.objects.create(
            account=account,
            first_name=form.cleaned_data['first_name'].strip(),
            last_name=form.cleaned_data['last_name'].strip(),
            phone=form.cleaned_data.get('phone', '').strip() or '',
        )
        request.session['account_id'] = account.id
        messages.success(request, 'Регистрация прошла успешно. Добро пожаловать!')
        return redirect('core:home')
    return render(request, 'accounts/auth/register.html', {'form': form})


def logout_view(request):
    request.session.flush()
    messages.info(request, 'Вы вышли из аккаунта.')
    return redirect('core:home')


def profile_view(request):
    account = get_current_account(request)
    if not account:
        messages.error(request, 'Для просмотра профиля необходимо войти.')
        return redirect('accounts:login')

    profile = None
    stats = None
    try:
        profile = account.profile
    except UserProfile.DoesNotExist:
        pass

    if account.role and account.role.name == 'admin':
        from apps.catalog.models import Equipment, EquipmentCategory, Manufacturer
        from apps.leasing.models import Company, LeaseContract, PaymentSchedule, Maintenance, MaintenanceRequest

        stats = {
            'accounts': Account.objects.count(),
            'roles': Role.objects.count(),
            'companies': Company.objects.count(),
            'equipment': Equipment.objects.count(),
            'categories': EquipmentCategory.objects.count(),
            'manufacturers': Manufacturer.objects.count(),
            'contracts': LeaseContract.objects.count(),
            'contracts_active': LeaseContract.objects.filter(status='active').count(),
            'payments': PaymentSchedule.objects.count(),
            'payments_pending': PaymentSchedule.objects.filter(status='pending').count(),
            'maintenance': Maintenance.objects.count(),
            'maintenance_requests': MaintenanceRequest.objects.count(),
            'maintenance_requests_new': MaintenanceRequest.objects.filter(status='new').count(),
        }

    return render(request, 'accounts/profile.html', {
        'account': account,
        'profile': profile,
        'stats': stats,
        'is_admin': account.role and account.role.name == 'admin',
    })
