from django import template

from apps.core.media_urls import extract_first_image_url, resolve_static_image_url

register = template.Library()


@register.filter
def get_item(d, key):
    """Получить элемент словаря по ключу."""
    if d is None:
        return None
    return d.get(key)


@register.filter
def first_image_url(value):
    """Первый URL картинки из JSONField и корректный префикс для локальной статики."""
    return resolve_static_image_url(extract_first_image_url(value))
