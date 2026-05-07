from django.db import models
from django.db.models import Q


class Role(models.Model):
    """Роли пользователей (1 к М с аккаунтами)."""
    name = models.CharField(max_length=50, unique=True)
    permissions = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'role'
        verbose_name = 'роль'
        verbose_name_plural = 'роли'

    def __str__(self):
        return self.name


class Account(models.Model):
    """Аккаунты (основная таблица входа)."""
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.ForeignKey(
        Role,
        on_delete=models.RESTRICT,
        related_name='accounts',
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'account'
        verbose_name = 'аккаунт'
        verbose_name_plural = 'аккаунты'

    def __str__(self):
        return self.username

    @property
    def is_authenticated(self):
        return True


class UserProfile(models.Model):
    """Профили пользователей (1 к 1 с аккаунтом)."""
    account = models.OneToOneField(
        Account,
        on_delete=models.CASCADE,
        related_name='profile',
        unique=True,
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    passport_series = models.CharField(max_length=4, blank=True)
    passport_number = models.CharField(max_length=6, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profile'
        verbose_name = 'профиль пользователя'
        verbose_name_plural = 'профили пользователей'
        constraints = [
            models.UniqueConstraint(
                fields=['passport_series', 'passport_number'],
                condition=~Q(passport_series='') & ~Q(passport_number=''),
                name='uniq_user_profile_passport_pair',
            ),
        ]

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class AccountToken(models.Model):
    """Токен для авторизации через API (привязка к Account)."""
    key = models.CharField(max_length=64, unique=True, db_index=True)
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='api_tokens',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'account_token'
        verbose_name = 'токен API'
        verbose_name_plural = 'токены API'

    def __str__(self):
        return f'{self.account.username} — {self.key[:8]}...'
