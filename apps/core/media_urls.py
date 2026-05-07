"""
Разбор поля images_urls (JSONField): списки URL, строка, JSON внутри строки.

- /media/... — загрузки с панели (MEDIA), отдаются как есть.
- /static/... — встроенная статика; при manifest — через static().
"""
from __future__ import annotations

import json

from django.conf import settings
from django.templatetags.static import static


def extract_first_image_url(images_value):
    """Возвращает первый URL изображения из JSONField (list/tuple/str)."""
    if images_value is None:
        return ''
    if isinstance(images_value, (list, tuple)):
        if not images_value:
            return ''
        return _stringify_url_item(images_value[0])
    if isinstance(images_value, str):
        text = images_value.strip()
        if not text:
            return ''
        if text.startswith(('[', '{')) or (text.startswith('"') and text.endswith('"') and len(text) > 1):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, (list, tuple)):
                    return _stringify_url_item(parsed[0]) if parsed else ''
                if isinstance(parsed, str):
                    return parsed.strip()
            except json.JSONDecodeError:
                pass
        return text
    if isinstance(images_value, dict):
        for key in ('url', 'src', '0'):
            if key in images_value:
                return _stringify_url_item(images_value[key])
        return ''
    return str(images_value).strip()


def _stringify_url_item(item):
    if item is None:
        return ''
    if isinstance(item, str):
        s = item.strip()
        if s.startswith('['):
            try:
                inner = json.loads(s)
                if isinstance(inner, (list, tuple)) and inner:
                    return str(inner[0]).strip()
            except json.JSONDecodeError:
                pass
        return s
    return str(item).strip()


def resolve_static_image_url(url: str) -> str:
    """
    Пути из БД: /media/... без изменений; /static/... через static() при manifest.
    Внешние http(s) и protocol-relative оставляет без изменений.
    """
    if not url:
        return ''
    u = url.strip()
    if u.startswith(('http://', 'https://', '//')):
        return u
    media_url = (getattr(settings, 'MEDIA_URL', None) or '/media/').rstrip('/') + '/'
    if u.startswith(media_url) or u == media_url.rstrip('/'):
        return u
    prefix = '/static/'
    if u.startswith(prefix):
        rel = u[len(prefix):].lstrip('/')
        try:
            return static(rel)
        except (ValueError, LookupError):
            # Новые файлы после upload ещё не в manifest до collectstatic — не падаем с 500.
            base = (getattr(settings, 'STATIC_URL', None) or '/static/').rstrip('/')
            return f'{base}/{rel}' if rel else base + '/'
    return u
