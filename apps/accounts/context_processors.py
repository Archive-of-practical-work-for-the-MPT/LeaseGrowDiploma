from .views import get_current_account


def current_account(request):
    """Добавляет текущий аккаунт и флаг is_admin в контекст всех шаблонов."""
    account = get_current_account(request)
    is_admin = bool(account and account.role and account.role.name == 'admin')
    return {'current_account': account, 'is_admin': is_admin}
