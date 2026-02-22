from rest_framework import serializers
from apps.leasing.models import (
    Company, LeaseContract,
    PaymentSchedule, MaintenanceRequest,
)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class LeaseContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaseContract
        fields = '__all__'


class PaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSchedule
        fields = '__all__'


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRequest
        fields = '__all__'
