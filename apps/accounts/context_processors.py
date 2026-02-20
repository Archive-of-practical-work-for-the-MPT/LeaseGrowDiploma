from .views import get_current_account


def current_account(request):
    """Добавляет текущий аккаунт, is_admin, is_manager и списки для панели."""
    account = get_current_account(request)
    is_admin = bool(account and account.role and account.role.name == 'admin')
    is_manager = bool(account and account.role and account.role.name == 'manager')

    # Для панели управления — какие таблицы показывать менеджеру
    from apps.control_panel.mixins import MANAGER_ALLOWED_KEYS
    if is_manager and request.path.startswith('/control-panel/'):
        control_panel_model_keys = MANAGER_ALLOWED_KEYS
        control_panel_show_audit = False
    else:
        control_panel_model_keys = None
        control_panel_show_audit = is_admin

    return {
        'current_account': account,
        'is_admin': is_admin,
        'is_manager': is_manager,
        'control_panel_model_keys': control_panel_model_keys,
        'control_panel_show_audit': control_panel_show_audit,
    }
