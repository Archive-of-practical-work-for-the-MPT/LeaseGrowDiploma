from django.contrib import admin
from .models import (
    Company, LeaseContract,
    PaymentSchedule, MaintenanceRequest,
    LeaseRequest, ChatMessage, MaintenanceChatMessage,
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'inn', 'status', 'account')
    list_filter = ('status',)


@admin.register(LeaseContract)
class LeaseContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'company', 'equipment', 'status', 'start_date')


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ('contract', 'payment_number', 'due_date', 'amount', 'status')


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


@admin.register(MaintenanceChatMessage)
class MaintenanceChatMessageAdmin(admin.ModelAdmin):
    list_display = ('maintenance_request', 'sender', 'created_at')
