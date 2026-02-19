from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly

from apps.accounts.models import Role, Account, UserProfile, AccountToken
from .serializers import (
    RoleSerializer,
    AccountSerializer,
    UserProfileSerializer,
    AccountTokenSerializer,
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
    queryset = AccountToken.objects.all()
    serializer_class = AccountTokenSerializer

    def get_queryset(self):
        if getattr(self.request, 'user', None) and hasattr(self.request.user, 'id'):
            return AccountToken.objects.filter(account=self.request.user)
        return AccountToken.objects.none()

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticatedOrReadOnly()]
        return [IsAuthenticated()]
