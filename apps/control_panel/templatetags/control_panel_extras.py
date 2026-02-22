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


@register.simple_tag
def sort_url(query_string, sort_by, sort_dir, field_name):
    """
    Возвращает query string для сортировки по field_name.
    При повторном клике по той же колонке переключает asc/desc.
    """
    from urllib.parse import parse_qs, urlencode
    params = parse_qs(query_string) if query_string else {}
    params.pop('page', None)
    params['sort_by'] = [field_name]
    if sort_by == field_name and sort_dir == 'asc':
        params['sort_dir'] = ['desc']
    else:
        params['sort_dir'] = ['asc']
    flat = {}
    for k, v in params.items():
        flat[k] = v[0] if v else ''
    return urlencode(flat)


@register.filter
def get_field(obj, field_name):
    """Возвращает значение поля объекта по имени."""
    if field_name in ('password_hash', 'password'):
        return '****'
    try:
        return getattr(obj, field_name, None)
    except Exception:
        return None
