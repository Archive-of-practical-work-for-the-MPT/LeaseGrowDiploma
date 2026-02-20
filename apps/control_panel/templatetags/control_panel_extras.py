from django import template

register = template.Library()


@register.filter
def get_field(obj, field_name):
    """Возвращает значение поля объекта по имени."""
    if field_name in ('password_hash', 'password'):
        return '****'
    try:
        return getattr(obj, field_name, None)
    except Exception:
        return None
