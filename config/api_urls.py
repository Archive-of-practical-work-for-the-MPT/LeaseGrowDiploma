"""Объединённый API — все роутеры из приложений."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.leasing.api.views import api_root
from apps.accounts.api.viewsets import (
    RoleViewSet, AccountViewSet, UserProfileViewSet, AccountTokenViewSet,
)
from apps.catalog.api.viewsets import (
    EquipmentCategoryViewSet, ManufacturerViewSet, EquipmentViewSet,
)
from apps.leasing.api.viewsets import (
    CompanyViewSet, LeaseContractViewSet,
    PaymentScheduleViewSet, MaintenanceRequestViewSet,
)
from apps.core.api.viewsets import AuditLogViewSet

router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'user-profiles', UserProfileViewSet, basename='userprofile')
router.register(r'account-tokens', AccountTokenViewSet, basename='accounttoken')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'equipment-categories', EquipmentCategoryViewSet, basename='equipmentcategory')
router.register(r'manufacturers', ManufacturerViewSet, basename='manufacturer')
router.register(r'equipment', EquipmentViewSet, basename='equipment')
router.register(r'lease-contracts', LeaseContractViewSet, basename='leasecontract')
router.register(r'payment-schedules', PaymentScheduleViewSet, basename='paymentschedule')
router.register(r'maintenance-requests', MaintenanceRequestViewSet, basename='maintenancerequest')
router.register(r'audit-logs', AuditLogViewSet, basename='auditlog')

urlpatterns = [
    path('', api_root),
    path('', include(router.urls)),
]
