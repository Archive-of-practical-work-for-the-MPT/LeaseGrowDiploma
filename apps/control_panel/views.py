"""Представления панели управления администратора."""
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView
from django.views import View
from django.contrib import messages

from apps.accounts.models import Role, Account, UserProfile, AccountToken
from apps.catalog.models import EquipmentCategory, Manufacturer, Equipment
from apps.leasing.models import (
    Company, CompanyContact, LeaseContract, PaymentSchedule,
    Maintenance, MaintenanceRequest,
)
from apps.core.models import AuditLog

from .mixins import AdminOrManagerRequiredMixin
from .forms import (
    RoleForm, AccountForm, UserProfileForm, AccountTokenForm,
    EquipmentCategoryForm, ManufacturerForm, EquipmentForm,
    CompanyForm, CompanyContactForm, LeaseContractForm,
    PaymentScheduleForm, MaintenanceForm, MaintenanceRequestForm,
)


PANEL_MODELS = [
    ('role', Role, 'Роли', 'control_panel:role_list'),
    ('account', Account, 'Аккаунты', 'control_panel:account_list'),
    ('userprofile', UserProfile, 'Профили', 'control_panel:userprofile_list'),
    ('accounttoken', AccountToken, 'Токены API', 'control_panel:accounttoken_list'),
    ('equipmentcategory', EquipmentCategory, 'Категории техники',
     'control_panel:equipmentcategory_list'),
    ('manufacturer', Manufacturer, 'Производители',
     'control_panel:manufacturer_list'),
    ('equipment', Equipment, 'Техника', 'control_panel:equipment_list'),
    ('company', Company, 'Компании', 'control_panel:company_list'),
    ('companycontact', CompanyContact, 'Контакты компаний',
     'control_panel:companycontact_list'),
    ('leasecontract', LeaseContract, 'Договоры лизинга',
     'control_panel:leasecontract_list'),
    ('paymentschedule', PaymentSchedule, 'Графики платежей',
     'control_panel:paymentschedule_list'),
    ('maintenance', Maintenance, 'Обслуживание', 'control_panel:maintenance_list'),
    ('maintenancerequest', MaintenanceRequest,
     'Заявки на обслуживание', 'control_panel:maintenancerequest_list'),
]


class DashboardView(AdminOrManagerRequiredMixin, View):
    """Главная страница панели управления."""

    def get(self, request):
        account = getattr(request, 'current_account', None)
        if account and account.role and account.role.name == 'manager':
            from .mixins import MANAGER_ALLOWED_KEYS
            models = [m for m in PANEL_MODELS if m[0] in MANAGER_ALLOWED_KEYS]
        else:
            models = PANEL_MODELS
        return render(request, 'control_panel/dashboard.html', {
            'models': models,
            'show_audit': account and account.role and account.role.name == 'admin',
        })


def _make_list_view(model, model_key, title, form_class=None):
    _model, _model_key, _title = model, model_key, title

    class V(AdminOrManagerRequiredMixin, ListView):
        model = _model
        template_name = 'control_panel/list.html'
        context_object_name = 'items'
        paginate_by = 10

        def get_context_data(self, **kwargs):
            ctx = super().get_context_data(**kwargs)
            ctx['model_key'] = _model_key
            ctx['title'] = _title
            ctx['create_url'] = f'control_panel:{_model_key}_create'
            ctx['edit_url_name'] = f'control_panel:{_model_key}_edit'
            ctx['delete_url_name'] = f'control_panel:{_model_key}_delete'
            pk_name = _model._meta.pk.name
            ctx['full_fields'] = [
                (f.name, f.verbose_name or f.name)
                for f in _model._meta.fields
                if f.name != pk_name
            ]
            return ctx
    return V


def _make_create_view(model, model_key, title, form_class):
    _model, _model_key, _title, _form_class = model, model_key, title, form_class

    class V(AdminOrManagerRequiredMixin, CreateView):
        model = _model
        form_class = _form_class
        template_name = 'control_panel/form.html'

        def get_context_data(self, **kwargs):
            ctx = super().get_context_data(**kwargs)
            ctx['model_key'] = _model_key
            ctx['title'] = f'Добавить: {_title}'
            ctx['list_url'] = f'control_panel:{_model_key}_list'
            ctx['submit_label'] = 'Создать'
            return ctx

        def get_success_url(self):
            messages.success(self.request, 'Запись создана.')
            return reverse(f'control_panel:{_model_key}_list')
    return V


def _make_update_view(model, model_key, title, form_class):
    _model, _model_key, _title, _form_class = model, model_key, title, form_class

    class V(AdminOrManagerRequiredMixin, UpdateView):
        model = _model
        form_class = _form_class
        template_name = 'control_panel/form.html'
        context_object_name = 'obj'
        pk_url_kwarg = 'pk'

        def get_context_data(self, **kwargs):
            ctx = super().get_context_data(**kwargs)
            ctx['model_key'] = _model_key
            ctx['title'] = f'Редактировать: {_title}'
            ctx['list_url'] = f'control_panel:{_model_key}_list'
            ctx['submit_label'] = 'Сохранить'
            ctx['delete_url'] = f'control_panel:{_model_key}_delete'
            return ctx

        def get_success_url(self):
            messages.success(self.request, 'Изменения сохранены.')
            return reverse(f'control_panel:{_model_key}_list')
    return V


def _make_delete_view(model, model_key, title):
    _model, _model_key = model, model_key

    class V(AdminOrManagerRequiredMixin, View):
        def post(self, request, pk):
            obj = get_object_or_404(_model, pk=pk)
            obj.delete()
            messages.success(request, 'Запись удалена.')
            return redirect(f'control_panel:{_model_key}_list')
    return V


# --- View классы ---

class RoleListView(_make_list_view(Role, 'role', 'Роли')):
    pass


class RoleCreateView(_make_create_view(Role, 'role', 'Роль', RoleForm)):
    pass


class RoleUpdateView(_make_update_view(Role, 'role', 'Роль', RoleForm)):
    pass


class RoleDeleteView(_make_delete_view(Role, 'role', 'Роль')):
    pass


class AccountListView(_make_list_view(Account, 'account', 'Аккаунты')):
    pass


class AccountCreateView(_make_create_view(Account, 'account', 'Аккаунт', AccountForm)):
    pass


class AccountUpdateView(_make_update_view(Account, 'account', 'Аккаунт', AccountForm)):
    pass


class AccountDeleteView(_make_delete_view(Account, 'account', 'Аккаунт')):
    pass


class UserProfileListView(_make_list_view(UserProfile, 'userprofile', 'Профили')):
    pass


class UserProfileCreateView(_make_create_view(UserProfile, 'userprofile', 'Профиль', UserProfileForm)):
    pass


class UserProfileUpdateView(_make_update_view(UserProfile, 'userprofile', 'Профиль', UserProfileForm)):
    pass


class UserProfileDeleteView(_make_delete_view(UserProfile, 'userprofile', 'Профиль')):
    pass


class AccountTokenListView(_make_list_view(AccountToken, 'accounttoken', 'Токены API')):
    pass


class AccountTokenCreateView(_make_create_view(AccountToken, 'accounttoken', 'Токен', AccountTokenForm)):
    pass


class AccountTokenUpdateView(_make_update_view(AccountToken, 'accounttoken', 'Токен', AccountTokenForm)):
    pass


class AccountTokenDeleteView(_make_delete_view(AccountToken, 'accounttoken', 'Токен')):
    pass


class EquipmentCategoryListView(_make_list_view(EquipmentCategory, 'equipmentcategory', 'Категории')):
    pass


class EquipmentCategoryCreateView(_make_create_view(
    EquipmentCategory, 'equipmentcategory', 'Категорию', EquipmentCategoryForm
)):
    pass


class EquipmentCategoryUpdateView(_make_update_view(
    EquipmentCategory, 'equipmentcategory', 'Категорию', EquipmentCategoryForm
)):
    pass


class EquipmentCategoryDeleteView(_make_delete_view(EquipmentCategory, 'equipmentcategory', 'Категорию')):
    pass


class ManufacturerListView(_make_list_view(Manufacturer, 'manufacturer', 'Производители')):
    pass


class ManufacturerCreateView(_make_create_view(Manufacturer, 'manufacturer', 'Производителя', ManufacturerForm)):
    pass


class ManufacturerUpdateView(_make_update_view(Manufacturer, 'manufacturer', 'Производителя', ManufacturerForm)):
    pass


class ManufacturerDeleteView(_make_delete_view(Manufacturer, 'manufacturer', 'Производитель')):
    pass


class EquipmentListView(_make_list_view(Equipment, 'equipment', 'Техника')):
    pass


class EquipmentCreateView(_make_create_view(Equipment, 'equipment', 'Технику', EquipmentForm)):
    pass


class EquipmentUpdateView(_make_update_view(Equipment, 'equipment', 'Технику', EquipmentForm)):
    pass


class EquipmentDeleteView(_make_delete_view(Equipment, 'equipment', 'Техника')):
    pass


class CompanyListView(_make_list_view(Company, 'company', 'Компании')):
    pass


class CompanyCreateView(_make_create_view(Company, 'company', 'Компанию', CompanyForm)):
    pass


class CompanyUpdateView(_make_update_view(Company, 'company', 'Компанию', CompanyForm)):
    pass


class CompanyDeleteView(_make_delete_view(Company, 'company', 'Компания')):
    pass


class CompanyContactListView(_make_list_view(CompanyContact, 'companycontact', 'Контакты')):
    pass


class CompanyContactCreateView(_make_create_view(
    CompanyContact, 'companycontact', 'Контакт', CompanyContactForm
)):
    pass


class CompanyContactUpdateView(_make_update_view(
    CompanyContact, 'companycontact', 'Контакт', CompanyContactForm
)):
    pass


class CompanyContactDeleteView(_make_delete_view(CompanyContact, 'companycontact', 'Контакт')):
    pass


class LeaseContractListView(_make_list_view(LeaseContract, 'leasecontract', 'Договоры')):
    pass


class LeaseContractCreateView(_make_create_view(
    LeaseContract, 'leasecontract', 'Договор', LeaseContractForm
)):
    pass


class LeaseContractUpdateView(_make_update_view(
    LeaseContract, 'leasecontract', 'Договор', LeaseContractForm
)):
    pass


class LeaseContractDeleteView(_make_delete_view(LeaseContract, 'leasecontract', 'Договор')):
    pass


class PaymentScheduleListView(_make_list_view(PaymentSchedule, 'paymentschedule', 'Платежи')):
    pass


class PaymentScheduleCreateView(_make_create_view(
    PaymentSchedule, 'paymentschedule', 'Платёж', PaymentScheduleForm
)):
    pass


class PaymentScheduleUpdateView(_make_update_view(
    PaymentSchedule, 'paymentschedule', 'Платёж', PaymentScheduleForm
)):
    pass


class PaymentScheduleDeleteView(_make_delete_view(PaymentSchedule, 'paymentschedule', 'Платёж')):
    pass


class MaintenanceListView(_make_list_view(Maintenance, 'maintenance', 'Обслуживание')):
    pass


class MaintenanceCreateView(_make_create_view(Maintenance, 'maintenance', 'Обслуживание', MaintenanceForm)):
    pass


class MaintenanceUpdateView(_make_update_view(Maintenance, 'maintenance', 'Обслуживание', MaintenanceForm)):
    pass


class MaintenanceDeleteView(_make_delete_view(Maintenance, 'maintenance', 'Обслуживание')):
    pass


class MaintenanceRequestListView(_make_list_view(MaintenanceRequest, 'maintenancerequest', 'Заявки')):
    pass


class MaintenanceRequestCreateView(_make_create_view(
    MaintenanceRequest, 'maintenancerequest', 'Заявку', MaintenanceRequestForm
)):
    pass


class MaintenanceRequestUpdateView(_make_update_view(
    MaintenanceRequest, 'maintenancerequest', 'Заявку', MaintenanceRequestForm
)):
    pass


class MaintenanceRequestDeleteView(_make_delete_view(MaintenanceRequest, 'maintenancerequest', 'Заявка')):
    pass


class AuditLogListView(AdminOrManagerRequiredMixin, ListView):
    """Журнал аудита — только чтение."""
    model = AuditLog
    template_name = 'control_panel/audit_list.html'
    context_object_name = 'items'
    paginate_by = 10
    ordering = ['-performed_at']

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Журнал аудита'
        return ctx
