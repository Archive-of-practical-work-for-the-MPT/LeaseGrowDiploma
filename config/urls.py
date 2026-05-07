"""
Корневой URL-конфиг LeaseGrow.
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic.base import RedirectView
from django.views.static import serve

handler404 = 'apps.core.views.page_not_found'

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/core/images/favicons/favicon.ico', permanent=True)),
    re_path(
        r'^media/(?P<path>.*)$',
        serve,
        {'document_root': settings.MEDIA_ROOT},
    ),
    path('', include('apps.core.urls')),
    path('', include('apps.accounts.urls')),
    path('control-panel/', include('apps.control_panel.urls')),
    path('manager/', include('apps.manager.urls')),
    path('chat/', include('apps.leasing.chat_urls')),
    path('api/', include('config.api_urls')),
    path('admin/', admin.site.urls),
]
