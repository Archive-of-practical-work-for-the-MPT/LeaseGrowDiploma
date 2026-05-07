"""WhiteNoise для production: сжатые файлы из STATIC_ROOT после collectstatic."""

STORAGES_WHITENOISE_COMPRESSED_MANIFEST = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}
