import os
import subprocess
import tempfile
from datetime import datetime
from django.conf import settings
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages

from .models import Account, UserProfile, Role
from .forms import LoginForm, RegisterForm, ProfileEditForm


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
        profile = None

    form = ProfileEditForm(
        account=account,
        initial={
            'username': account.username,
            'email': account.email,
            'first_name': profile.first_name if profile else '',
            'last_name': profile.last_name if profile else '',
            'phone': profile.phone if profile else '',
        } if request.method != 'POST' else None,
        data=request.POST if request.method == 'POST' else None,
    )

    is_client = not (account.role and account.role.name in ('admin', 'manager'))
    if is_client and request.method == 'POST' and form.is_valid():
        account.username = form.cleaned_data['username'].strip()
        account.email = form.cleaned_data['email'].strip().lower()
        account.save(update_fields=['username', 'email', 'updated_at'])
        if form.cleaned_data.get('new_password'):
            account.password_hash = make_password(form.cleaned_data['new_password'])
            account.save(update_fields=['password_hash'])

        if profile:
            profile.first_name = form.cleaned_data['first_name'].strip()
            profile.last_name = form.cleaned_data['last_name'].strip()
            profile.phone = (form.cleaned_data.get('phone') or '').strip()
            profile.save(update_fields=['first_name', 'last_name', 'phone', 'updated_at'])
        else:
            UserProfile.objects.create(
                account=account,
                first_name=form.cleaned_data['first_name'].strip(),
                last_name=form.cleaned_data['last_name'].strip(),
                phone=(form.cleaned_data.get('phone') or '').strip(),
            )
        messages.success(request, 'Профиль обновлён.')
        return redirect('accounts:profile')

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

    is_manager = account.role and account.role.name == 'manager'
    return render(request, 'accounts/profile.html', {
        'account': account,
        'profile': profile,
        'form': form,
        'stats': stats,
        'is_admin': account.role and account.role.name == 'admin',
        'is_manager': is_manager,
    })


def backup_view(request):
    account = get_current_account(request)
    if not account:
        messages.error(request, 'Войдите в систему.')
        return redirect('accounts:login')
    if not account.role or account.role.name != 'admin':
        messages.error(request, 'Доступ только для администратора.')
        return redirect('accounts:profile')

    db = settings.DATABASES['default']
    if db['ENGINE'] != 'django.db.backends.postgresql':
        messages.error(request, 'Бэкап поддерживается только для PostgreSQL.')
        return redirect('accounts:profile')

    # Создание бэкапа
    if request.method == 'POST' and request.POST.get('action') == 'create':
        try:
            with tempfile.NamedTemporaryFile(
                mode='wb', suffix='.sql', delete=False
            ) as tmp:
                tmp_path = tmp.name

            env = os.environ.copy()
            env['PGPASSWORD'] = db.get('PASSWORD', '')
            env['PGCLIENTENCODING'] = 'UTF8'

            pg_bin = getattr(settings, 'PG_BIN_PATH', '') or ''
            pg_dump_exe = 'pg_dump.exe' if os.name == 'nt' else 'pg_dump'
            pg_dump_cmd = os.path.join(pg_bin, pg_dump_exe) if pg_bin else 'pg_dump'

            cmd = [
                pg_dump_cmd,
                '-h', db.get('HOST', 'localhost'),
                '-p', str(db.get('PORT', 5432)),
                '-U', db.get('USER', 'postgres'),
                '-d', db.get('NAME', ''),
                '--encoding=UTF8',
                '--clean',
                '--if-exists',
                '-F', 'p',
                '-f', tmp_path,
            ]

            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                os.unlink(tmp_path)
                messages.error(
                    request,
                    f'Ошибка pg_dump: {result.stderr or result.stdout}',
                )
                return redirect('accounts:backup')

            filename = f'leasegrow_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sql'
            with open(tmp_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/sql; charset=utf-8')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
            os.unlink(tmp_path)
            return response

        except FileNotFoundError:
            messages.error(
                request,
                'pg_dump не найден. Убедитесь, что PostgreSQL установлен и путь к bin добавлен в PATH.',
            )
        except subprocess.TimeoutExpired:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            messages.error(request, 'Превышено время ожидания создания бэкапа.')
        except Exception as e:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            messages.error(request, f'Ошибка: {str(e)}')
        return redirect('accounts:backup')

    # Восстановление из загруженного файла
    if request.method == 'POST' and request.POST.get('action') == 'restore':
        uploaded_file = request.FILES.get('backup_file')
        if not uploaded_file:
            messages.error(request, 'Выберите файл бэкапа.')
            return redirect('accounts:backup')

        if not uploaded_file.name.lower().endswith('.sql'):
            messages.error(request, 'Разрешены только файлы .sql')
            return redirect('accounts:backup')

        try:
            with tempfile.NamedTemporaryFile(
                mode='wb', suffix='.sql', delete=False
            ) as tmp:
                for chunk in uploaded_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            env = os.environ.copy()
            env['PGPASSWORD'] = db.get('PASSWORD', '')
            env['PGCLIENTENCODING'] = 'UTF8'

            pg_bin = getattr(settings, 'PG_BIN_PATH', '') or ''
            psql_exe = 'psql.exe' if os.name == 'nt' else 'psql'
            psql_cmd = os.path.join(pg_bin, psql_exe) if pg_bin else 'psql'

            cmd = [
                psql_cmd,
                '-v', 'ON_ERROR_STOP=1',
                '-h', db.get('HOST', 'localhost'),
                '-p', str(db.get('PORT', 5432)),
                '-U', db.get('USER', 'postgres'),
                '-d', db.get('NAME', ''),
                '-f', tmp_path,
            ]

            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=600,
            )

            os.unlink(tmp_path)

            if result.returncode != 0:
                messages.error(
                    request,
                    f'Ошибка восстановления: {result.stderr or result.stdout}',
                )
            else:
                messages.success(request, 'Бэкап успешно восстановлен.')

        except FileNotFoundError:
            messages.error(
                request,
                'psql не найден. Убедитесь, что PostgreSQL установлен и путь к bin добавлен в PATH.',
            )
        except subprocess.TimeoutExpired:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            messages.error(request, 'Превышено время ожидания восстановления.')
        except Exception as e:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
            messages.error(request, f'Ошибка: {str(e)}')
        return redirect('accounts:backup')

    return render(request, 'accounts/backup.html', {'is_admin': True})
