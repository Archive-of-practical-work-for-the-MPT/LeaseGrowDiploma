from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('404-preview/', views.page_404_preview, name='404_preview'),
    path('leasing/', views.leasing, name='leasing'),
    path('my-equipment/', views.my_equipment, name='my_equipment'),
    path('my-maintenance/', views.my_maintenance_requests, name='my_maintenance_requests'),
    path('leasing/request/<int:equipment_id>/', views.leasing_request_create, name='leasing_request_create'),
    path('contract/<int:pk>/sign/', views.contract_sign, name='contract_sign'),
    path('contract/<int:pk>/pay/', views.contract_pay, name='contract_pay'),
    path('contract/<int:pk>/maintenance/', views.maintenance_request_create, name='maintenance_request_create'),
    path('privacy/', views.privacy, name='privacy'),
    path('about/', views.about, name='about'),
]
