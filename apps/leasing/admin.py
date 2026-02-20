from django.contrib import admin
from .models import (
    Company, CompanyContact, LeaseContract,
    PaymentSchedule, Maintenance, MaintenanceRequest,
    LeaseRequest, ChatMessage,
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'inn', 'status', 'account')
    list_filter = ('status',)


@admin.register(CompanyContact)
class CompanyContactAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'company', 'is_main', 'phone')


@admin.register(LeaseContract)
class LeaseContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'company', 'equipment', 'status', 'start_date')


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ('contract', 'payment_number', 'due_date', 'amount', 'status')


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'type', 'performed_at', 'cost')


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'company', 'urgency', 'status')


@admin.register(LeaseRequest)
class LeaseRequestAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'account', 'status', 'created_at')
    list_filter = ('status',)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('lease_request', 'sender', 'created_at')
