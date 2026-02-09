"""
ViewSet'ы для REST API по таблицам БД.
Все поля, CRUD. Авторизация — через таблицу account_tokens (POST = вход).
"""
from rest_framework import viewsets
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly,
)

from core.models import (
    Role, Account, UserProfile, AccountToken,
    Company, CompanyContact,
    EquipmentCategory, Manufacturer, Equipment,
    LeaseContract, PaymentSchedule,
    Maintenance, MaintenanceRequest,
    AuditLog,
)
from core.api.serializers import (
    RoleSerializer,
    AccountSerializer,
    UserProfileSerializer,
    AccountTokenSerializer,
    CompanySerializer,
    CompanyContactSerializer,
    EquipmentCategorySerializer,
    ManufacturerSerializer,
    EquipmentSerializer,
    LeaseContractSerializer,
    PaymentScheduleSerializer,
    MaintenanceSerializer,
    MaintenanceRequestSerializer,
    AuditLogSerializer,
)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.select_related('role').all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.select_related('account').all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class AccountTokenViewSet(viewsets.ModelViewSet):
    """
    Токены доступа. POST с {username, password} = вход (создаётся токен).
    GET/DELETE требуют заголовок Authorization: Token <key>.
    """
    queryset = AccountToken.objects.all()
    serializer_class = AccountTokenSerializer

    def get_queryset(self):
        if getattr(self.request, 'user', None) and hasattr(
            self.request.user, 'id'
        ):
            return AccountToken.objects.filter(account=self.request.user)
        return AccountToken.objects.none()

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticatedOrReadOnly()]
        return [IsAuthenticated()]


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().prefetch_related('contacts')
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CompanyContactViewSet(viewsets.ModelViewSet):
    queryset = CompanyContact.objects.all()
    serializer_class = CompanyContactSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class EquipmentCategoryViewSet(viewsets.ModelViewSet):
    queryset = EquipmentCategory.objects.all()
    serializer_class = EquipmentCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.select_related(
        'category', 'manufacturer'
    ).all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class LeaseContractViewSet(viewsets.ModelViewSet):
    queryset = (
        LeaseContract.objects
        .select_related('company', 'equipment')
        .prefetch_related('payment_schedule')
        .all()
    )
    serializer_class = LeaseContractSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PaymentScheduleViewSet(viewsets.ModelViewSet):
    queryset = PaymentSchedule.objects.select_related('contract').all()
    serializer_class = PaymentScheduleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class MaintenanceViewSet(viewsets.ModelViewSet):
    queryset = Maintenance.objects.select_related('equipment').all()
    serializer_class = MaintenanceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRequest.objects.select_related(
        'equipment', 'company'
    ).all()
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Журнал аудита — только чтение."""
    queryset = AuditLog.objects.all().order_by('-performed_at')
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
