from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.db.models import Q

from apps.accounts.models import Role, Account, UserProfile, AccountToken


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        min_length=8, write_only=True, required=False, allow_blank=True
    )

    class Meta:
        model = Account
        fields = (
            'id', 'email', 'username', 'password', 'password_hash',
            'role', 'is_active', 'last_login',
            'created_at', 'updated_at',
        )
        extra_kwargs = {'password_hash': {'read_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if password:
            validated_data['password_hash'] = make_password(password)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            validated_data['password_hash'] = make_password(password)
        return super().update(instance, validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class AccountTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = AccountToken
        fields = ('id', 'key', 'account', 'created_at', 'username', 'password')
        extra_kwargs = {'key': {'read_only': True}}

    def create(self, validated_data):
        import secrets
        from django.contrib.auth.hashers import check_password

        username = validated_data.pop('username', None)
        password = validated_data.pop('password', None)
        if username is not None and password is not None:
            account = Account.objects.filter(
                Q(email__iexact=username.strip())
                | Q(username__iexact=username.strip()),
                is_active=True,
            ).first()
            if not account or not check_password(password, account.password_hash):
                raise serializers.ValidationError(
                    'Неверный логин или пароль.'
                )
            validated_data['account'] = account
        if 'account' not in validated_data:
            raise serializers.ValidationError(
                'Укажите account или пару username и password.'
            )
        validated_data['key'] = secrets.token_hex(32)
        return super().create(validated_data)
