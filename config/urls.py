"""
Корневой URL-конфиг LeaseGrow.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('apps.core.urls')),
    path('', include('apps.accounts.urls')),
    path('api/', include('config.api_urls')),
    path('admin/', admin.site.urls),
]
