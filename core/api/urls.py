from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .viewsets import (
    RoleViewSet,
    AccountViewSet,
    UserProfileViewSet,
    AccountTokenViewSet,
    CompanyViewSet,
    CompanyContactViewSet,
    EquipmentCategoryViewSet,
    ManufacturerViewSet,
    EquipmentViewSet,
    LeaseContractViewSet,
    PaymentScheduleViewSet,
    MaintenanceViewSet,
    MaintenanceRequestViewSet,
    AuditLogViewSet,
)

app_name = 'api'

router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'user-profiles', UserProfileViewSet, basename='userprofile')
router.register(r'account-tokens', AccountTokenViewSet, basename='accounttoken')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(
    r'company-contacts', CompanyContactViewSet, basename='companycontact'
)
router.register(
    r'equipment-categories',
    EquipmentCategoryViewSet,
    basename='equipmentcategory',
)
router.register(r'manufacturers', ManufacturerViewSet, basename='manufacturer')
router.register(r'equipment', EquipmentViewSet, basename='equipment')
router.register(
    r'lease-contracts', LeaseContractViewSet, basename='leasecontract'
)
router.register(
    r'payment-schedules',
    PaymentScheduleViewSet,
    basename='paymentschedule',
)
router.register(r'maintenances', MaintenanceViewSet, basename='maintenance')
router.register(
    r'maintenance-requests',
    MaintenanceRequestViewSet,
    basename='maintenancerequest',
)
router.register(r'audit-logs', AuditLogViewSet, basename='auditlog')

urlpatterns = [
    path('', views.api_root),
    path('', include(router.urls)),
]
