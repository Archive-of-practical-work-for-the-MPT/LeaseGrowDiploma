from django.db import models
from decimal import Decimal


# --- Роли и аккаунты ---

class Role(models.Model):
    """Роли пользователей (1 к М с аккаунтами)."""
    name = models.CharField(max_length=50, unique=True)  # 'client', 'manager', 'admin', 'accountant'
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=list, blank=True)  # список прав
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
        """Для совместимости с DRF permission IsAuthenticated."""
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


# --- Компании и клиенты ---

class Company(models.Model):
    """Компании (клиенты)."""
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('blocked', 'Заблокирована'),
        ('pending', 'На модерации'),
    ]
    name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=500, blank=True)
    inn = models.CharField(max_length=12, unique=True)
    kpp = models.CharField(max_length=9, blank=True)
    ogrn = models.CharField(max_length=15, blank=True)
    legal_address = models.TextField(blank=True)
    actual_address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    bank_details = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=50, default='active', choices=STATUS_CHOICES)
    account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='companies',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'company'
        verbose_name = 'компания'
        verbose_name_plural = 'компании'

    def __str__(self):
        return self.name


class CompanyContact(models.Model):
    """Контактные лица компаний."""
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='contacts',
    )
    full_name = models.CharField(max_length=255)
    position = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'company_contact'
        verbose_name = 'контакт компании'
        verbose_name_plural = 'контакты компаний'

    def __str__(self):
        return self.full_name


# --- Сельхозтехника ---

class EquipmentCategory(models.Model):
    """Категории техники (иерархия)."""
    name = models.CharField(max_length=150)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
    )
    description = models.TextField(blank=True)
    icon_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'equipment_category'
        verbose_name = 'категория техники'
        verbose_name_plural = 'категории техники'

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    """Производители техники."""
    name = models.CharField(max_length=255, unique=True)
    country = models.CharField(max_length=100, blank=True)
    website = models.URLField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    logo_url = models.URLField(max_length=500, blank=True)

    class Meta:
        db_table = 'manufacturer'
        verbose_name = 'производитель'
        verbose_name_plural = 'производители'

    def __str__(self):
        return self.name


class Equipment(models.Model):
    """Техника (основная таблица)."""
    CONDITION_CHOICES = [
        ('new', 'Новая'),
        ('used', 'Б/У'),
        ('refurbished', 'Восстановленная'),
    ]
    STATUS_CHOICES = [
        ('available', 'Доступна'),
        ('leased', 'В лизинге'),
        ('maintenance', 'На обслуживании'),
        ('sold', 'Продана'),
    ]
    name = models.CharField(max_length=255)
    model = models.CharField(max_length=150)
    category = models.ForeignKey(
        EquipmentCategory,
        on_delete=models.RESTRICT,
        related_name='equipment',
    )
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipment',
    )
    specifications = models.JSONField(default=dict)
    year = models.IntegerField(null=True, blank=True)
    vin = models.CharField(max_length=100, unique=True, null=True, blank=True)
    condition = models.CharField(max_length=50, default='new', choices=CONDITION_CHOICES)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    residual_value = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    monthly_lease_rate = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    status = models.CharField(max_length=50, default='available', choices=STATUS_CHOICES)
    location = models.CharField(max_length=500, blank=True)
    images_urls = models.JSONField(default=list, blank=True)  # список URL
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'equipment'
        verbose_name = 'техника'
        verbose_name_plural = 'техника'

    def __str__(self):
        return f'{self.name} ({self.model})'


# --- Лизинг и договоры ---

class LeaseContract(models.Model):
    """Договоры лизинга."""
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('active', 'Действует'),
        ('completed', 'Завершён'),
        ('terminated', 'Расторгнут'),
    ]
    contract_number = models.CharField(max_length=100, unique=True)
    company = models.ForeignKey(
        Company,
        on_delete=models.RESTRICT,
        related_name='lease_contracts',
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.RESTRICT,
        related_name='lease_contracts',
    )
    start_date = models.DateField()
    end_date = models.DateField()
    lease_term_months = models.IntegerField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    advance_payment = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2)
    payment_day = models.IntegerField(default=1)
    status = models.CharField(max_length=50, default='draft', choices=STATUS_CHOICES)
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_by = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='signed_contracts',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_contracts',
    )

    class Meta:
        db_table = 'lease_contract'
        verbose_name = 'договор лизинга'
        verbose_name_plural = 'договоры лизинга'

    def __str__(self):
        return self.contract_number


class PaymentSchedule(models.Model):
    """График платежей (1 к М с договором)."""
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('paid', 'Оплачен'),
        ('overdue', 'Просрочен'),
        ('cancelled', 'Отменён'),
    ]
    contract = models.ForeignKey(
        LeaseContract,
        on_delete=models.CASCADE,
        related_name='payment_schedule',
    )
    payment_number = models.IntegerField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='pending', choices=STATUS_CHOICES)
    paid_at = models.DateTimeField(null=True, blank=True)
    penalty_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0')
    )

    class Meta:
        db_table = 'payment_schedule'
        verbose_name = 'платёж по графику'
        verbose_name_plural = 'графики платежей'
        constraints = [
            models.UniqueConstraint(
                fields=['contract', 'payment_number'],
                name='unique_contract_payment_number',
            ),
        ]

    def __str__(self):
        return f'{self.contract.contract_number} — платёж #{self.payment_number}'


# --- Обслуживание и заявки ---

class Maintenance(models.Model):
    """Обслуживание техники."""
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='maintenances',
    )
    type = models.CharField(max_length=100)  # 'техобслуживание', 'ремонт', 'диагностика'
    description = models.TextField(blank=True)
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    performed_at = models.DateField()
    next_maintenance_date = models.DateField(null=True, blank=True)
    service_company = models.CharField(max_length=255, blank=True)
    documents_urls = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintenance_records',
    )

    class Meta:
        db_table = 'maintenance'
        verbose_name = 'обслуживание'
        verbose_name_plural = 'обслуживание'

    def __str__(self):
        return f'{self.equipment} — {self.type} ({self.performed_at})'


class MaintenanceRequest(models.Model):
    """Заявки на техобслуживание."""
    URGENCY_CHOICES = [
        ('low', 'Низкий'),
        ('normal', 'Обычный'),
        ('high', 'Высокий'),
        ('critical', 'Критичный'),
    ]
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('completed', 'Выполнена'),
        ('cancelled', 'Отменена'),
    ]
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='maintenance_requests',
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='maintenance_requests',
    )
    description = models.TextField()
    urgency = models.CharField(max_length=50, default='normal', choices=URGENCY_CHOICES)
    status = models.CharField(max_length=50, default='new', choices=STATUS_CHOICES)
    assigned_to = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_maintenance_requests',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'maintenance_request'
        verbose_name = 'заявка на обслуживание'
        verbose_name_plural = 'заявки на обслуживание'

    def __str__(self):
        return f'Заявка #{self.id} — {self.equipment}'


# --- Аудит ---

class AuditLog(models.Model):
    """Журнал аудита."""
    action = models.CharField(max_length=100)  # 'CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT'
    table_name = models.CharField(max_length=100)
    record_id = models.IntegerField()
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    changed_fields = models.JSONField(default=list, blank=True)  # список полей
    performed_by = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    performed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        db_table = 'audit_log'
        verbose_name = 'запись аудита'
        verbose_name_plural = 'журнал аудита'
        indexes = [
            models.Index(fields=['table_name', 'record_id'], name='idx_audit_table_record'),
            models.Index(fields=['performed_at'], name='idx_audit_performed_at'),
        ]
        ordering = ['-performed_at']

    def __str__(self):
        return f'{self.action} {self.table_name}.{self.record_id}'
