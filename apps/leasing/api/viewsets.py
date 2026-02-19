from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.leasing.models import (
    Company, CompanyContact, LeaseContract,
    PaymentSchedule, Maintenance, MaintenanceRequest,
)
from .serializers import (
    CompanySerializer,
    CompanyContactSerializer,
    LeaseContractSerializer,
    PaymentScheduleSerializer,
    MaintenanceSerializer,
    MaintenanceRequestSerializer,
)


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().prefetch_related('contacts')
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CompanyContactViewSet(viewsets.ModelViewSet):
    queryset = CompanyContact.objects.all()
    serializer_class = CompanyContactSerializer
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
