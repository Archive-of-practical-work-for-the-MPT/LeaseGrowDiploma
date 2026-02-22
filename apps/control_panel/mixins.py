"""Миксины для проверки доступа к панели управления."""
from django.shortcuts import redirect
from django.contrib import messages

from apps.accounts.views import get_current_account

# Таблицы, доступные менеджеру (admin видит все)
MANAGER_ALLOWED_KEYS = frozenset([
    'account', 'userprofile', 'equipmentcategory', 'equipment',
    'company', 'companycontact', 'leasecontract', 'paymentschedule',
    'maintenance', 'maintenancerequest',
])


class AdminRequiredMixin:
    """Требует роль администратора."""

    def dispatch(self, request, *args, **kwargs):
        account = get_current_account(request)
        if not account:
            messages.error(request, 'Для доступа требуется авторизация.')
            return redirect('accounts:login')
        if not account.role or account.role.name != 'admin':
            messages.error(
                request, 'Доступ запрещён. Требуется роль администратора.'
            )
            return redirect('core:home')
        request.current_account = account
        return super().dispatch(request, *args, **kwargs)


class AdminOrManagerRequiredMixin:
    """Требует роль администратора или менеджера. Ограничивает менеджера по таблицам."""

    def dispatch(self, request, *args, **kwargs):
        account = get_current_account(request)
        if not account:
            messages.error(request, 'Для доступа требуется авторизация.')
            return redirect('accounts:login')
        if not account.role or account.role.name not in ('admin', 'manager'):
            messages.error(
                request, 'Доступ запрещён. Требуется роль администратора или менеджера.'
            )
            return redirect('core:home')
        request.current_account = account

        # Менеджеру доступны только MANAGER_ALLOWED_KEYS
        if account.role.name == 'manager':
            url_name = request.resolver_match.url_name
            model_key = None
            if url_name == 'audit_list':
                model_key = 'audit'
            elif url_name == 'lease_request_create_contract':
                model_key = None  # разрешено менеджеру
            elif url_name and '_' in url_name:
                model_key = url_name.split('_', 1)[0]
                if model_key in ('dashboard',):
                    model_key = None
            if model_key and model_key not in MANAGER_ALLOWED_KEYS:
                messages.error(request, 'Доступ к этой таблице запрещён.')
                return redirect('control_panel:dashboard')

        return super().dispatch(request, *args, **kwargs)
