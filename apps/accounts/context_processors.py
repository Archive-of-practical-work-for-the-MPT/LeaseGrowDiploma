from .views import get_current_account


def current_account(request):
    """Добавляет текущий аккаунт в контекст всех шаблонов."""
    return {'current_account': get_current_account(request)}
