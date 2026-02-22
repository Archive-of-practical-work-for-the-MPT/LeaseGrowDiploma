"""
Функциональные тесты: CRUD операции над моделями LeaseGrow.
Запуск: из папки LeaseGrow выполнить
  python manage.py test tests.test_crud
"""
from decimal import Decimal
from django.contrib.auth.hashers import make_password
from django.test import TestCase

from apps.accounts.models import Role, Account, UserProfile
from apps.catalog.models import EquipmentCategory, Manufacturer, Equipment
from apps.leasing.models import LeaseRequest


class RoleCRUDTest(TestCase):
    """Функциональный тест: CRUD для модели Role (роль)."""

    def test_role_crud(self):
        """CRUD для роли (Role): создание, чтение, обновление, удаление."""
        # Create
        role = Role.objects.create(
            name='test_role',
            description='Тестовая роль',
            permissions=['own_contracts'],
        )
        self.assertIsNotNone(role.id)
        self.assertEqual(role.name, 'test_role')

        # Read
        found = Role.objects.get(name='test_role')
        self.assertEqual(found.id, role.id)

        # Update
        role.name = 'updated_role'
        role.save()
        found.refresh_from_db()
        self.assertEqual(found.name, 'updated_role')

        # Delete
        pk = role.id
        role.delete()
        self.assertFalse(Role.objects.filter(pk=pk).exists())


class AccountCRUDTest(TestCase):
    """Функциональный тест: CRUD для модели Account (аккаунт)."""

    def setUp(self):
        self.role = Role.objects.create(name='client', description='Клиент')

    def test_account_crud(self):
        """CRUD для аккаунта (Account): создание, чтение, обновление, удаление."""
        # Create
        account = Account.objects.create(
            email='test@test.ru',
            username='testuser',
            password_hash=make_password('pass123'),
            role=self.role,
        )
        self.assertIsNotNone(account.id)
        self.assertEqual(account.username, 'testuser')

        # Read
        found = Account.objects.get(username='testuser')
        self.assertEqual(found.email, 'test@test.ru')

        # Update
        account.username = 'updated_user'
        account.save()
        found.refresh_from_db()
        self.assertEqual(found.username, 'updated_user')

        # Delete
        pk = account.id
        account.delete()
        self.assertFalse(Account.objects.filter(pk=pk).exists())


class EquipmentCRUDTest(TestCase):
    """Функциональный тест: CRUD для модели Equipment (техника)."""

    def setUp(self):
        self.category = EquipmentCategory.objects.create(
            name='Тракторы',
            description='Сельхозтехника',
        )
        self.manufacturer = Manufacturer.objects.create(
            name='John Deere',
            country='США',
        )

    def test_equipment_crud(self):
        """CRUD для техники (Equipment): создание, чтение, обновление, удаление."""
        # Create
        equipment = Equipment.objects.create(
            name='Тестовый трактор',
            model='8R',
            category=self.category,
            manufacturer=self.manufacturer,
            price=Decimal('10000000'),
            monthly_lease_rate=Decimal('100000'),
            status='available',
            vin='TEST123',
        )
        self.assertIsNotNone(equipment.id)
        self.assertEqual(equipment.name, 'Тестовый трактор')

        # Read
        found = Equipment.objects.get(vin='TEST123')
        self.assertEqual(found.model, '8R')

        # Update
        equipment.name = 'Обновлённый трактор'
        equipment.save()
        found.refresh_from_db()
        self.assertEqual(found.name, 'Обновлённый трактор')

        # Delete
        pk = equipment.id
        equipment.delete()
        self.assertFalse(Equipment.objects.filter(pk=pk).exists())


class LeaseRequestCRUDTest(TestCase):
    """Функциональный тест: CRUD для модели LeaseRequest (заявка на лизинг)."""

    def setUp(self):
        self.role = Role.objects.create(name='client', description='Клиент')
        self.account = Account.objects.create(
            email='client@test.ru',
            username='testclient',
            password_hash=make_password('pass'),
            role=self.role,
        )
        self.category = EquipmentCategory.objects.create(name='Тракторы')
        self.manufacturer = Manufacturer.objects.create(name='Deere')
        self.equipment = Equipment.objects.create(
            name='Трактор',
            model='8R',
            category=self.category,
            manufacturer=self.manufacturer,
            price=Decimal('10000000'),
            status='available',
            vin='VIN001',
        )

    def test_lease_request_crud(self):
        """CRUD для заявки на лизинг (LeaseRequest): создание, чтение, обновление, удаление."""
        # Create
        lease_req = LeaseRequest.objects.create(
            equipment=self.equipment,
            account=self.account,
            status='pending',
            message='Хочу в лизинг',
        )
        self.assertIsNotNone(lease_req.id)
        self.assertEqual(lease_req.status, 'pending')

        # Read
        found = LeaseRequest.objects.get(equipment=self.equipment, account=self.account)
        self.assertEqual(found.message, 'Хочу в лизинг')

        # Update
        lease_req.status = 'confirmed'
        lease_req.save()
        found.refresh_from_db()
        self.assertEqual(found.status, 'confirmed')

        # Delete
        pk = lease_req.id
        lease_req.delete()
        self.assertFalse(LeaseRequest.objects.filter(pk=pk).exists())
