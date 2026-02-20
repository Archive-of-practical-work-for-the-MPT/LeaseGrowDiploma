"""
Корневой URL-конфиг LeaseGrow.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('apps.core.urls')),
    path('', include('apps.accounts.urls')),
    path('control-panel/', include('apps.control_panel.urls')),
    path('manager/', include('apps.manager.urls')),
    path('api/', include('config.api_urls')),
    path('admin/', admin.site.urls),
]
