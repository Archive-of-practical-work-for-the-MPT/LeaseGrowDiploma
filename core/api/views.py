"""
Корень API — список эндпоинтов по таблицам БД.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """Список API по таблицам БД."""
    base = request.build_absolute_uri('/api/').rstrip('/')
    return Response({
        'roles': f'{base}/roles/',
        'accounts': f'{base}/accounts/',
        'user_profiles': f'{base}/user-profiles/',
        'account_tokens': f'{base}/account-tokens/',
        'companies': f'{base}/companies/',
        'company_contacts': f'{base}/company-contacts/',
        'equipment_categories': f'{base}/equipment-categories/',
        'manufacturers': f'{base}/manufacturers/',
        'equipment': f'{base}/equipment/',
        'lease_contracts': f'{base}/lease-contracts/',
        'payment_schedules': f'{base}/payment-schedules/',
        'maintenances': f'{base}/maintenances/',
        'maintenance_requests': f'{base}/maintenance-requests/',
        'audit_logs': f'{base}/audit-logs/',
    })
