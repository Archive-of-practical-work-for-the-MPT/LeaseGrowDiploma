from django.db import models


class Role(models.Model):
    """Роли пользователей (1 к М с аккаунтами)."""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
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
    is_verified = models.BooleanField(default=False)
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
    avatar_url = models.URLField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    preferred_language = models.CharField(max_length=10, default='ru')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profile'
        verbose_name = 'профиль пользователя'
        verbose_name_plural = 'профили пользователей'

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
