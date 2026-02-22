"""
Настройки для локальной разработки.
"""
from .base import *

# DEBUG берётся из .env (base.py). Для проверки 404 поставьте DEBUG=False в .env
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
