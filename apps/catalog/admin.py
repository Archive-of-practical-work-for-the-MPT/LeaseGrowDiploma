from django.contrib import admin
from .models import EquipmentCategory, Manufacturer, Equipment


@admin.register(EquipmentCategory)
class EquipmentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'created_at')


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'category', 'status', 'price')
    list_filter = ('status', 'condition', 'category')
