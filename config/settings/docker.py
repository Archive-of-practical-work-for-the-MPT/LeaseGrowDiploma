"""
Настройки для запуска в Docker.
Импортирует base и переопределяет параметры для контейнера.
"""
from .base import *  # noqa: F401, F403
from .whitenoise_storages import STORAGES_WHITENOISE_COMPRESSED_MANIFEST

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])  # noqa: F405

# Production-статика: только из STATIC_ROOT после collectstatic (WhiteNoise, manifest + сжатие).
STORAGES = STORAGES_WHITENOISE_COMPRESSED_MANIFEST

# EMAIL_BACKEND уже правильно настроен в base.py для SMTP отправки писем
