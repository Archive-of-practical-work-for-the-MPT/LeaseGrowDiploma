from django.contrib import admin
from .models import Role, Account, UserProfile, AccountToken


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'created_at')
    list_filter = ('is_active', 'role')
    search_fields = ('username', 'email')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('account', 'first_name', 'last_name', 'phone')


@admin.register(AccountToken)
class AccountTokenAdmin(admin.ModelAdmin):
    list_display = ('account', 'key', 'created_at')
