"""ASGI routing for WebSockets."""
from django.urls import re_path

from apps.leasing import consumers

websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<request_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'^ws/maintenance-chat/(?P<maint_id>\d+)/$', consumers.MaintenanceChatConsumer.as_asgi()),
]
