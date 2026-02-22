import json

from django import template

register = template.Library()


@register.filter
def json_dump(value):
    """Сериализует значение в JSON-строку для отображения."""
    if value is None:
        return ''
    try:
        return json.dumps(value, ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        return str(value)


@register.filter
def get_field(obj, field_name):
    """Возвращает значение поля объекта по имени."""
    if field_name in ('password_hash', 'password'):
        return '****'
    try:
        return getattr(obj, field_name, None)
    except Exception:
        return None
