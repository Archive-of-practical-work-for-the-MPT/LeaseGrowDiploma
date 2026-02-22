from django.urls import path

from . import views

app_name = 'manager'

urlpatterns = [
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
    path('admin-statistics/', views.AdminStatisticsView.as_view(), name='admin_statistics'),
    path('statistics/export/excel/', views.StatisticsExportExcelView.as_view(), name='statistics_export_excel'),
    path('statistics/export/pdf/', views.StatisticsExportPdfView.as_view(), name='statistics_export_pdf'),
    path('chat/', views.ChatView.as_view(), name='chat'),
    path('maintenance-chat/', views.MaintenanceChatView.as_view(), name='maintenance_chat'),
    path('lease-request/<int:pk>/create-contract/', views.LeaseRequestCreateContractView.as_view(), name='lease_request_create_contract'),
]
