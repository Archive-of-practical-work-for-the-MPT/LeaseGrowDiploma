from django.urls import path

from . import views

app_name = 'manager'

urlpatterns = [
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
    path('statistics/export/excel/', views.StatisticsExportExcelView.as_view(), name='statistics_export_excel'),
    path('statistics/export/pdf/', views.StatisticsExportPdfView.as_view(), name='statistics_export_pdf'),
    path('chat/', views.ChatView.as_view(), name='chat'),
]
