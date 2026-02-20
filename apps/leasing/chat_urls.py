from django.urls import path

from . import chat_views

app_name = 'chat'

urlpatterns = [
    path('<int:request_id>/', chat_views.chat_thread, name='thread'),
]
