"""Утилиты для записи в журнал аудита при CRUD операциях в панели."""

from apps.core.models import AuditLog


def _serialize_value(value):
    """Сериализует значение поля для хранения в JSON."""
    if value is None:
        return None
    if hasattr(value, 'pk'):
        return value.pk
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, dict)):
        return value
    return str(value)


def model_instance_to_dict(instance):
    """Преобразует экземпляр модели в словарь для записи в audit_log."""
    if instance is None:
        return None
    result = {}
    for f in instance._meta.fields:
        try:
            val = getattr(instance, f.name, None)
            result[f.name] = _serialize_value(val)
        except Exception:
            result[f.name] = None
    return result


def log_audit(
    action,
    table_name,
    record_id,
    request=None,
    old_values=None,
    new_values=None,
    changed_fields=None,
):
    """
    Записывает операцию в журнал аудита.

    action: 'INSERT' | 'UPDATE' | 'DELETE'
    table_name: имя таблицы (db_table или verbose_name модели)
    record_id: ID записи
    request: HttpRequest (для performed_by)
    old_values: dict (для UPDATE/DELETE)
    new_values: dict (для INSERT/UPDATE)
    changed_fields: list (для UPDATE — список изменённых полей)
    """
    performed_by = None
    if request and hasattr(request, 'current_account'):
        performed_by = getattr(request, 'current_account', None)

    AuditLog.objects.create(
        action=action,
        table_name=str(table_name)[:100],
        record_id=int(record_id),
        old_values=old_values,
        new_values=new_values,
        changed_fields=changed_fields or [],
        performed_by=performed_by,
    )
