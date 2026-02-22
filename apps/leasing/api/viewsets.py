from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.leasing.models import (
    Company, LeaseContract,
    PaymentSchedule, MaintenanceRequest,
)
from .serializers import (
    CompanySerializer,
    LeaseContractSerializer,
    PaymentScheduleSerializer,
    MaintenanceRequestSerializer,
)


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
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


class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRequest.objects.select_related(
        'equipment', 'company'
    ).all()
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
