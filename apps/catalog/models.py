from django.db import models


class EquipmentCategory(models.Model):
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
    specifications = models.TextField(blank=True, default='')
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
    images_urls = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'equipment'
        verbose_name = 'техника'
        verbose_name_plural = 'техника'

    def __str__(self):
        return f'{self.name} ({self.model})'
