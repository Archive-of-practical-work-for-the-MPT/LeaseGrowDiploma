"""
Интеграционные тесты: REST API LeaseGrow (техника, компании, аутентификация).
Запуск: из папки LeaseGrow выполнить
  python manage.py test tests.test_api
"""
from decimal import Decimal
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Account, Role, UserProfile, AccountToken
from apps.catalog.models import EquipmentCategory, Manufacturer, Equipment
from apps.leasing.models import Company


def _login_as_admin(client):
    """Создаёт роль ADMIN, аккаунт, профиль и авторизует сессию для доступа к API."""
    role = Role.objects.create(
        name='admin',
        description='Администратор',
        permissions=['all'],
    )
    account = Account.objects.create(
        email='admin@test.local',
        username='admin',
        password_hash=make_password('adminpass'),
        role=role,
    )
    UserProfile.objects.create(account=account, first_name='Admin', last_name='Test')
    session = client.session
    session['account_id'] = account.id
    session.save()
    return account


def _create_api_token(account):
    """Создаёт токен API для аккаунта."""
    return AccountToken.objects.create(
        key='test-token-12345678901234567890123456789012',
        account=account,
    )


class ApiRootTest(TestCase):
    """Интеграционный тест: корень API возвращает 200."""

    def setUp(self):
        self.client = APIClient()

    def test_api_root_ok(self):
        """GET /api/ — корень API доступен."""
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EquipmentAPITest(TestCase):
    """Интеграционный тест: API техники (список, создание, чтение по id)."""

    def setUp(self):
        self.client = APIClient()
        _login_as_admin(self.client)
        token = _create_api_token(Account.objects.get(username='admin'))
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.category = EquipmentCategory.objects.create(
            name='Тракторы',
            description='Тест',
        )
        self.manufacturer = Manufacturer.objects.create(
            name='John Deere',
            country='США',
        )
        Equipment.objects.create(
            name='Test Tractor',
            model='8R',
            category=self.category,
            manufacturer=self.manufacturer,
            price=Decimal('10000000'),
            monthly_lease_rate=Decimal('100000'),
            status='available',
            vin='TEST123',
        )

    def test_equipment_list_and_detail(self):
        """API техники: список (GET), чтение по id (GET)."""
        url_list = reverse('equipment-list')
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data['results'] if isinstance(data, dict) and 'results' in data else (data if isinstance(data, list) else [])
        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Test Tractor')

        equipment_id = Equipment.objects.get(vin='TEST123').id
        url_detail = reverse('equipment-detail', kwargs={'pk': equipment_id})
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['model'], '8R')


class CompaniesAPITest(TestCase):
    """Интеграционный тест: API компаний (список)."""

    def setUp(self):
        self.client = APIClient()
        account = _login_as_admin(self.client)
        token = _create_api_token(account)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        Company.objects.create(
            name='Тестовая компания',
            inn='1234567890',
            status='active',
            account=account,
        )

    def test_companies_list(self):
        """API компаний: список (GET)."""
        url_list = reverse('company-list')
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data['results'] if isinstance(data, dict) and 'results' in data else (data if isinstance(data, list) else [])
        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Тестовая компания')


class ApiAuthTest(TestCase):
    """Интеграционный тест: API аутентификация по токену."""

    def setUp(self):
        self.client = APIClient()
        role = Role.objects.create(name='admin', permissions=['all'])
        self.account = Account.objects.create(
            email='admin@test.local',
            username='admin',
            password_hash=make_password('pass'),
            role=role,
        )

    def test_invalid_token_rejected(self):
        """Неверный токен — 401/403."""
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid-token-xxx')
        response = self.client.get(reverse('equipment-list'))
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_valid_token_accepted(self):
        """Верный токен — доступ к API."""
        token = _create_api_token(self.account)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.get(reverse('equipment-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
