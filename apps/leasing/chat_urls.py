from django.urls import path

from . import chat_views

app_name = 'chat'

urlpatterns = [
    path('', chat_views.chat_list, name='list'),
    path('<int:request_id>/', chat_views.chat_thread, name='thread'),
]
