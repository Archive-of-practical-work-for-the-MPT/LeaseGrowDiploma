import logging
import os
import subprocess
import tempfile
from datetime import datetime, timedelta
from django.conf import settings
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.utils.crypto import constant_time_compare
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages

from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Account, UserProfile, Role
from .forms import (
    LoginForm, RegisterForm, ProfileEditForm,
    PasswordResetRequestForm, PasswordResetConfirmForm,
    ClientCompanyForm,
)

PASSWORD_RESET_TOKEN_MAX_AGE = 60 * 60
EMAIL_VERIFICATION_TOKEN_MAX_AGE = 60 * 60
EMAIL_VERIFICATION_RESEND_COOLDOWN = timedelta(minutes=3)

logger = logging.getLogger(__name__)


def get_current_account(request):
    """Возвращает аккаунт из сессии или None."""
    account_id = request.session.get('account_id')
    if not account_id:
        return None
    return Account.objects.filter(id=account_id, is_active=True).select_related('role').first()


def _make_email_verify_token(account_id):
    account = Account.objects.only('id', 'password_hash').get(id=account_id)
    signer = TimestampSigner()
    return signer.sign(f'{account.id}:{account.password_hash}')


def _get_account_from_email_verify_token(token, max_age=EMAIL_VERIFICATION_TOKEN_MAX_AGE):
    signer = TimestampSigner()
    try:
        value = signer.unsign(token, max_age=max_age)
        account_id, token_password_hash = value.split(':', 1)
        account = Account.objects.filter(id=int(account_id)).first()
        if account and constant_time_compare(account.password_hash, token_password_hash):
            return account
        return None
    except (SignatureExpired, BadSignature, ValueError):
        return None


def _send_verification_link_email(account, verify_url):
    subject = 'Подтверждение email — LeaseGrow'
    message = (
        f'Здравствуйте, {account.username}!\n\n'
        'Для подтверждения регистрации нажмите на кнопку (или перейдите по ссылке):\n\n'
        f'{verify_url}\n\n'
        'Ссылка действует 1 час.\n'
        'Если вы не регистрировались в LeaseGrow, просто проигнорируйте это письмо.'
    )
    html_message = render_to_string(
        'accounts/emails/email_verification.html',
        {'username': account.username, 'verify_url': verify_url},
    )
    email = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[account.email],
    )
    email.attach_alternative(html_message, 'text/html')
    email.send(
        fail_silently=False,
    )


def _send_registration_verification(request, account):
    token = _make_email_verify_token(account.id)
    verify_url = request.build_absolute_uri(
        reverse('accounts:activate_email', kwargs={'token': token})
    )
    _send_verification_link_email(account, verify_url)
    request.session['pending_verification_account_id'] = account.id
    request.session['email_verification_sent_at'] = timezone.now().isoformat()
    request.session.modified = True


def login_view(request):
    if get_current_account(request):
        return redirect('core:home')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username'].strip()
        password = form.cleaned_data['password']
        account = Account.objects.filter(
            Q(email__iexact=username) | Q(username__iexact=username),
        ).first()
        if account and check_password(password, account.password_hash):
            if not account.is_active:
                role_name = getattr(getattr(account, 'role', None), 'name', '')
                if role_name == 'client':
                    request.session['pending_verification_account_id'] = account.id
                    messages.warning(request, 'Подтвердите email по ссылке из письма.')
                    return redirect('accounts:verify_email')
                form.add_error(
                    None,
                    'Ваша учетная запись не активна. Обратитесь к администратору.',
                )
                return render(request, 'accounts/auth/login.html', {'form': form})
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
        try:
            with transaction.atomic():
                role_client, _ = Role.objects.get_or_create(name='client')
                account = Account.objects.create(
                    email=form.cleaned_data['email'].strip().lower(),
                    username=form.cleaned_data['username'].strip(),
                    password_hash=make_password(form.cleaned_data['password1']),
                    role=role_client,
                    is_active=False,
                )
                UserProfile.objects.create(
                    account=account,
                    first_name=form.cleaned_data['first_name'].strip(),
                    last_name=form.cleaned_data['last_name'].strip(),
                    phone=form.cleaned_data.get('phone', '').strip() or '',
                    passport_series=form.cleaned_data.get('passport_series', '').strip(),
                    passport_number=form.cleaned_data.get('passport_number', '').strip(),
                )
        except IntegrityError:
            logger.warning('register IntegrityError (race on unique email/username)')
            messages.error(
                request,
                'Пользователь с таким email или логином уже зарегистрирован. Попробуйте войти.',
            )
        except Exception:
            logger.exception('register: ошибка сохранения аккаунта в БД')
            messages.error(
                request,
                'Не удалось сохранить регистрацию. Попробуйте снова.',
            )
        else:
            try:
                _send_registration_verification(request, account)
            except Exception:
                logger.exception('register: не удалось отправить письмо подтверждения')
                request.session['pending_verification_account_id'] = account.id
                request.session.pop('email_verification_sent_at', None)
                request.session.modified = True
                messages.warning(
                    request,
                    'Аккаунт создан, но письмо не удалось отправить. '
                    'На следующей странице нажмите «Отправить письмо снова» или повторите позже.',
                )
                return redirect('accounts:verify_email')
            messages.success(
                request, 'Регистрация почти завершена: подтвердите email по ссылке из письма.')
            return redirect('accounts:verify_email')
    return render(request, 'accounts/auth/register.html', {'form': form})


def verify_email_view(request):
    if get_current_account(request):
        return redirect('core:home')

    account_id = request.session.get('pending_verification_account_id')
    if not account_id:
        messages.info(request, 'Нет ожидающего подтверждения email. Выполните вход.')
        return redirect('accounts:login')

    account = Account.objects.filter(id=account_id).first()
    if not account:
        request.session.pop('pending_verification_account_id', None)
        messages.error(request, 'Аккаунт для подтверждения не найден.')
        return redirect('accounts:register')

    if account.is_active:
        request.session.pop('pending_verification_account_id', None)
        request.session.pop('email_verification_sent_at', None)
        messages.success(request, 'Email уже подтверждён.')
        return redirect('accounts:login')
    now = timezone.now()
    seconds_until_resend = 0
    sent_at_raw = request.session.get('email_verification_sent_at')
    if sent_at_raw:
        try:
            sent_at = datetime.fromisoformat(sent_at_raw)
            if timezone.is_naive(sent_at):
                sent_at = timezone.make_aware(sent_at, timezone.get_current_timezone())
            resend_available_at = sent_at + EMAIL_VERIFICATION_RESEND_COOLDOWN
            seconds_until_resend = max(int((resend_available_at - now).total_seconds()), 0)
        except ValueError:
            request.session.pop('email_verification_sent_at', None)
    return render(request, 'accounts/auth/verify_email.html', {
        'account_email': account.email,
        'seconds_until_resend': seconds_until_resend,
    })


def resend_verification_code_view(request):
    if request.method != 'POST':
        return redirect('accounts:verify_email')

    account_id = request.session.get('pending_verification_account_id')
    if not account_id:
        messages.info(request, 'Нет ожидающего подтверждения email.')
        return redirect('accounts:login')

    account = Account.objects.filter(id=account_id).first()
    if not account:
        request.session.pop('pending_verification_account_id', None)
        messages.error(request, 'Аккаунт для подтверждения не найден.')
        return redirect('accounts:register')

    if account.is_active:
        request.session.pop('pending_verification_account_id', None)
        request.session.pop('email_verification_sent_at', None)
        messages.success(request, 'Email уже подтверждён.')
        return redirect('accounts:login')

    now = timezone.now()
    sent_at_raw = request.session.get('email_verification_sent_at')
    if sent_at_raw:
        try:
            sent_at = datetime.fromisoformat(sent_at_raw)
            if timezone.is_naive(sent_at):
                sent_at = timezone.make_aware(sent_at, timezone.get_current_timezone())
            next_allowed_at = sent_at + EMAIL_VERIFICATION_RESEND_COOLDOWN
            if now < next_allowed_at:
                seconds_left = int((next_allowed_at - now).total_seconds())
                messages.warning(
                    request,
                    f'Повторная отправка будет доступна через {seconds_left} сек.',
                )
                return redirect('accounts:verify_email')
        except ValueError:
            request.session.pop('email_verification_sent_at', None)

    _send_registration_verification(request, account)
    messages.success(request, 'Письмо с кнопкой подтверждения отправлено повторно.')
    return redirect('accounts:verify_email')


def activate_email_view(request, token):
    account = _get_account_from_email_verify_token(token)
    if not account:
        messages.error(request, 'Ссылка подтверждения недействительна или истекла.')
        return redirect('accounts:verify_email')

    if account.is_active:
        messages.info(request, 'Email уже подтвержден ранее.')
        return redirect('accounts:login')

    account.is_active = True
    account.save(update_fields=['is_active', 'updated_at'])
    request.session.pop('pending_verification_account_id', None)
    request.session.pop('email_verification_sent_at', None)
    request.session['account_id'] = account.id
    request.session['show_company_bind_prompt'] = True
    messages.success(request, 'Email подтверждён. Добро пожаловать!')
    return redirect('core:home')


def logout_view(request):
    request.session.flush()
    messages.info(request, 'Вы вышли из аккаунта.')
    return redirect('core:home')


def _make_reset_token(account_id):
    """Создаёт подписанный токен для сброса пароля на 1 час."""
    account = Account.objects.only('id', 'password_hash').get(id=account_id)
    signer = TimestampSigner()
    return signer.sign(f'{account.id}:{account.password_hash}')


def _get_account_from_token(token, max_age=PASSWORD_RESET_TOKEN_MAX_AGE):
    """Возвращает аккаунт, если ссылка не истекла и пароль ещё не менялся."""
    signer = TimestampSigner()
    try:
        value = signer.unsign(token, max_age=max_age)
        account_id, token_password_hash = value.split(':', 1)
        account = Account.objects.filter(id=int(account_id), is_active=True).first()
        if account and constant_time_compare(account.password_hash, token_password_hash):
            return account
        return None
    except (SignatureExpired, BadSignature, ValueError):
        return None


def password_reset_request_view(request):
    """Страница запроса сброса пароля — пользователь вводит email или логин."""
    if get_current_account(request):
        return redirect('core:home')
    form = PasswordResetRequestForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        value = form.cleaned_data['email_or_username'].strip()
        account = Account.objects.filter(
            Q(email__iexact=value) | Q(username__iexact=value),
            is_active=True,
        ).first()
        # Всегда показываем одно сообщение для защиты от перебора
        if account:
            token = _make_reset_token(account.id)
            reset_url = request.build_absolute_uri(
                reverse('accounts:password_reset_confirm',
                        kwargs={'token': token})
            )
            plain_message = (
                f'Здравствуйте, {account.username}!\n\n'
                f'Вы запросили сброс пароля. Перейдите по ссылке для установки нового пароля:\n\n'
                f'{reset_url}\n\n'
                f'Ссылка действительна 1 час.\n\n'
                f'Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.'
            )
            html_message = render_to_string(
                'accounts/emails/password_reset.html',
                {'username': account.username, 'reset_url': reset_url},
            )
            email = EmailMultiAlternatives(
                subject='Восстановление пароля — LeaseGrow',
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[account.email],
            )
            email.attach_alternative(html_message, 'text/html')
            email.send(fail_silently=False)
        messages.success(
            request,
            'Если аккаунт с таким email или логином существует, на почту отправлена ссылка для сброса пароля.'
        )
        return redirect('accounts:login')
    return render(request, 'accounts/auth/password_reset_request.html', {'form': form})


def password_reset_confirm_view(request, token):
    """Страница установки нового пароля по токену из письма."""
    if get_current_account(request):
        return redirect('core:home')
    account = _get_account_from_token(token)
    if not account:
        messages.error(
            request, 'Ссылка недействительна или истекла. Запросите сброс пароля снова.')
        return redirect('accounts:password_reset_request')
    form = PasswordResetConfirmForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        account.password_hash = make_password(form.cleaned_data['password1'])
        account.save(update_fields=['password_hash'])
        messages.success(
            request, 'Пароль успешно изменён. Войдите с новым паролем.')
        return redirect('accounts:login')
    return render(request, 'accounts/auth/password_reset_confirm.html', {'form': form, 'token': token})


def profile_view(request):
    account = get_current_account(request)
    if not account:
        messages.error(request, 'Для просмотра профиля необходимо войти.')
        return redirect('accounts:login')

    profile = None
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
            'passport_series': profile.passport_series if profile else '',
            'passport_number': profile.passport_number if profile else '',
        } if request.method != 'POST' else None,
        data=request.POST if request.method == 'POST' else None,
    )

    is_client = not (
        account.role and account.role.name in ('admin', 'manager'))
    if is_client and request.method == 'POST' and form.is_valid():
        account.username = form.cleaned_data['username'].strip()
        account.email = form.cleaned_data['email'].strip().lower()
        account.save(update_fields=['username', 'email', 'updated_at'])
        if form.cleaned_data.get('new_password'):
            account.password_hash = make_password(
                form.cleaned_data['new_password'])
            account.save(update_fields=['password_hash'])

        if profile:
            profile.first_name = form.cleaned_data['first_name'].strip()
            profile.last_name = form.cleaned_data['last_name'].strip()
            profile.phone = (form.cleaned_data.get('phone') or '').strip()
            profile.passport_series = (form.cleaned_data.get('passport_series') or '').strip()
            profile.passport_number = (form.cleaned_data.get('passport_number') or '').strip()
            profile.save(update_fields=[
                         'first_name', 'last_name', 'phone', 'passport_series', 'passport_number', 'updated_at'])
        else:
            UserProfile.objects.create(
                account=account,
                first_name=form.cleaned_data['first_name'].strip(),
                last_name=form.cleaned_data['last_name'].strip(),
                phone=(form.cleaned_data.get('phone') or '').strip(),
                passport_series=(form.cleaned_data.get('passport_series') or '').strip(),
                passport_number=(form.cleaned_data.get('passport_number') or '').strip(),
            )
        messages.success(request, 'Профиль обновлён.')
        return redirect('accounts:profile')

    is_manager = account.role and account.role.name == 'manager'
    is_client = not (
        account.role and account.role.name in ('admin', 'manager'))

    # Компания клиента (для заявок на лизинг)
    from apps.leasing.models import Company
    user_company = Company.objects.filter(account=account).first()
    company_form = None
    if is_client:
        initial_company = None
        if user_company and request.method != 'POST':
            initial_company = {
                'name': user_company.name,
                'inn': user_company.inn,
                'address': user_company.address or '',
                'phone': user_company.phone or '',
                'email': user_company.email or '',
            }
        company_form = ClientCompanyForm(
            instance=user_company,
            data=request.POST if request.method == 'POST' and request.POST.get(
                'form_type') == 'company' else None,
            initial=initial_company,
        )
        if request.method == 'POST' and request.POST.get('form_type') == 'company' and company_form.is_valid():
            data = company_form.cleaned_data
            if user_company:
                user_company.name = data['name'].strip()
                user_company.inn = data['inn'].strip()
                user_company.address = (data.get('address') or '').strip()
                user_company.phone = (data.get('phone') or '').strip()
                user_company.email = (data.get('email') or '').strip()
                user_company.save()
                messages.success(request, 'Данные компании обновлены.')
            else:
                Company.objects.create(
                    name=data['name'].strip(),
                    inn=data['inn'].strip(),
                    address=(data.get('address') or '').strip(),
                    phone=(data.get('phone') or '').strip(),
                    email=(data.get('email') or '').strip(),
                    status='active',
                    account=account,
                )
                messages.success(
                    request, 'Компания добавлена. Теперь вы можете оформить заявку на лизинг.')
            return redirect('accounts:profile')

    need_company = request.GET.get('need_company') == '1'
    return render(request, 'accounts/profile.html', {
        'account': account,
        'profile': profile,
        'form': form,
        'company_form': company_form,
        'user_company': user_company,
        'need_company': need_company,
        'is_admin': account.role and account.role.name == 'admin',
        'is_manager': is_manager,
        'is_client': is_client,
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
            pg_dump_cmd = os.path.join(
                pg_bin, pg_dump_exe) if pg_bin else 'pg_dump'

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
                response = HttpResponse(
                    f.read(), content_type='application/sql; charset=utf-8')
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
            messages.error(
                request, 'Превышено время ожидания создания бэкапа.')
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
