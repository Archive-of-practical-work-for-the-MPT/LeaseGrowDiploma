"""
Настройки для запуска в Docker.
Импортирует base и переопределяет параметры для контейнера.
"""
from .base import *  # noqa: F401, F403

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])  # noqa: F405
# EMAIL_BACKEND уже правильно настроен в base.py для SMTP отправки писем
