"""
Настройки для production.
"""
from .base import *

from .whitenoise_storages import STORAGES_WHITENOISE_COMPRESSED_MANIFEST

DEBUG = False
STORAGES = STORAGES_WHITENOISE_COMPRESSED_MANIFEST

# ALLOWED_HOSTS настраиваются через .env
