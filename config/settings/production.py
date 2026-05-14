"""
Настройки для production.
"""
from .base import *

from .whitenoise_storages import STORAGES_WHITENOISE_COMPRESSED_MANIFEST

DEBUG = False
STORAGES = STORAGES_WHITENOISE_COMPRESSED_MANIFEST

# ALLOWED_HOSTS и CSRF_TRUSTED_ORIGINS — из .env (списки через запятую)

# За Caddy/nginx с TLS до приложения идёт HTTP — иначе is_secure() и проверка CSRF ломаются.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# Редирект на HTTPS делает Caddy; при неверных заголовках возможны петли.
SECURE_SSL_REDIRECT = False
