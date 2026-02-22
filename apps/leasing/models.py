from django.db import models
from decimal import Decimal

from apps.accounts.models import Account
from apps.catalog.models import Equipment


class Company(models.Model):
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
    status = models.CharField(
        max_length=50, default='active', choices=STATUS_CHOICES)
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


class LeaseContract(models.Model):
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
    status = models.CharField(
        max_length=50, default='draft', choices=STATUS_CHOICES)
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
    lease_request = models.OneToOneField(
        'LeaseRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lease_contract',
    )

    class Meta:
        db_table = 'lease_contract'
        verbose_name = 'договор лизинга'
        verbose_name_plural = 'договоры лизинга'

    def __str__(self):
        return self.contract_number


class PaymentSchedule(models.Model):
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
    status = models.CharField(
        max_length=50, default='pending', choices=STATUS_CHOICES)
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


class Maintenance(models.Model):
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='maintenances',
    )
    type = models.CharField(max_length=100)
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
    urgency = models.CharField(
        max_length=50, default='normal', choices=URGENCY_CHOICES)
    status = models.CharField(
        max_length=50, default='new', choices=STATUS_CHOICES)
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


class MaintenanceChatMessage(models.Model):
    """Сообщение в чате по заявке на ТО."""
    maintenance_request = models.ForeignKey(
        MaintenanceRequest,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='maintenance_chat_messages',
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'maintenance_chat_message'
        verbose_name = 'сообщение чата ТО'
        verbose_name_plural = 'сообщения чата ТО'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender.username}: {self.text[:50]}...'


class LeaseRequest(models.Model):
    """Заявка пользователя на аренду техники. Подтверждается менеджером."""
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждена'),
        ('rejected', 'Отклонена'),
        ('cancelled', 'Отменена'),
    ]
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='lease_requests',
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='lease_requests',
    )
    status = models.CharField(
        max_length=50, default='pending', choices=STATUS_CHOICES)
    message = models.TextField(blank=True)
    manager_notes = models.TextField(blank=True)
    confirmed_by = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_lease_requests',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lease_request'
        verbose_name = 'заявка на лизинг'
        verbose_name_plural = 'заявки на лизинг'

    def __str__(self):
        return f'Заявка #{self.id} — {self.equipment} (пользователь: {self.account.username})'


class ChatMessage(models.Model):
    """Сообщение в чате по заявке на лизинг."""
    lease_request = models.ForeignKey(
        LeaseRequest,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='chat_messages',
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_message'
        verbose_name = 'сообщение чата'
        verbose_name_plural = 'сообщения чата'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender.username}: {self.text[:50]}...'
