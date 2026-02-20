from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('leasing/', views.leasing, name='leasing'),
    path('leasing/request/<int:equipment_id>/', views.leasing_request_create, name='leasing_request_create'),
    path('privacy/', views.privacy, name='privacy'),
]
