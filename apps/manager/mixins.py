"""Миксины для доступа менеджера."""
from django.shortcuts import redirect
from django.contrib import messages

from apps.accounts.views import get_current_account


class ManagerRequiredMixin:
    """Требует роль менеджера."""

    def dispatch(self, request, *args, **kwargs):
        account = get_current_account(request)
        if not account:
            messages.error(request, 'Для доступа требуется авторизация.')
            return redirect('accounts:login')
        if not account.role or account.role.name != 'manager':
            messages.error(
                request, 'Доступ запрещён. Требуется роль менеджера.'
            )
            return redirect('core:home')
        request.current_account = account
        return super().dispatch(request, *args, **kwargs)
