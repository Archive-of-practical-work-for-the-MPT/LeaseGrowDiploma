from django import template

register = template.Library()


@register.filter
def get_item(d, key):
    """Получить элемент словаря по ключу."""
    if d is None:
        return None
    return d.get(key)


@register.filter
def first_image_url(value):
    """Return a single image URL from either a list or a stored string."""
    if not value:
        return ''
    if isinstance(value, (list, tuple)):
        return value[0] if value else ''
    return value
