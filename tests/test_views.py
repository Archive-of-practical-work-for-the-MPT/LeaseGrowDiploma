"""
Интеграционные тесты: веб-страницы LeaseGrow (главная, логин, профиль, лизинг, чат).
Запуск: из папки LeaseGrow выполнить
  python manage.py test tests.test_views
"""
from decimal import Decimal
from django.contrib.auth.hashers import make_password
from django.test import TestCase, Client
from django.urls import reverse

from apps.accounts.models import Account, Role, UserProfile
from apps.catalog.models import EquipmentCategory, Manufacturer, Equipment
from apps.leasing.models import Company, LeaseRequest


def _login_as_client(client):
    """Создаёт клиента и авторизует сессию."""
    role = Role.objects.create(name='client', permissions=['own_contracts'])
    account = Account.objects.create(
        email='client@test.ru',
        username='testclient',
        password_hash=make_password('testpass123'),
        role=role,
    )
    UserProfile.objects.create(account=account, first_name='Тест', last_name='Клиент')
    session = client.session
    session['account_id'] = account.id
    session.save()
    return account


class HomePageTest(TestCase):
    """Интеграционный тест: главная страница."""

    def setUp(self):
        self.client = Client()

    def test_home_returns_200(self):
        """GET / — главная страница возвращает 200."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_home_contains_leasing_link(self):
        """Главная содержит ссылку на лизинг."""
        response = self.client.get('/')
        content = response.content.decode()
        self.assertTrue(
            'leasing' in content.lower() or 'лизинг' in content,
            'Страница должна содержать ссылку на лизинг',
        )


class AuthViewsTest(TestCase):
    """Интеграционный тест: авторизация (логин, логаут)."""

    def setUp(self):
        self.client = Client()
        self.role = Role.objects.create(name='client')
        self.account = Account.objects.create(
            email='client@test.ru',
            username='testclient',
            password_hash=make_password('testpass123'),
            role=self.role,
        )
        UserProfile.objects.create(account=self.account, first_name='Тест', last_name='Клиент')

    def test_login_page_ok(self):
        """GET /login/ — страница входа доступна."""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        """POST /login/ — успешный вход сохраняет account_id в сессии."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'client@test.ru',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get('account_id'), self.account.id)

    def test_logout_clears_session(self):
        """GET /logout/ — выход очищает сессию."""
        self.client.session['account_id'] = self.account.id
        self.client.session.save()
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('account_id', self.client.session)


class LeasingPageTest(TestCase):
    """Интеграционный тест: страница лизинга."""

    def setUp(self):
        self.client = Client()
        self.category = EquipmentCategory.objects.create(name='Тракторы')
        self.manufacturer = Manufacturer.objects.create(name='John Deere')
        self.equipment = Equipment.objects.create(
            name='Test Tractor',
            model='8R',
            category=self.category,
            manufacturer=self.manufacturer,
            price=Decimal('10000000'),
            status='available',
            vin='VIN001',
        )

    def test_leasing_page_ok(self):
        """GET /leasing/ — страница каталога лизинга доступна."""
        response = self.client.get(reverse('core:leasing'))
        self.assertEqual(response.status_code, 200)

    def test_leasing_shows_equipment(self):
        """Страница лизинга отображает технику."""
        response = self.client.get(reverse('core:leasing'))
        content = response.content.decode()
        self.assertIn('Test Tractor', content)


class ProfileAccessTest(TestCase):
    """Интеграционный тест: доступ к профилю."""

    def setUp(self):
        self.client = Client()

    def test_profile_redirects_if_not_logged_in(self):
        """Профиль без авторизации — редирект на логин."""
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_profile_ok_when_logged_in(self):
        """Профиль доступен после входа."""
        _login_as_client(self.client)
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)


class LeaseRequestFlowTest(TestCase):
    """Интеграционный тест: заявка на лизинг."""

    def setUp(self):
        self.client = Client()
        self.account = _login_as_client(self.client)
        Company.objects.create(
            name='Тестовая компания',
            inn='1234567890',
            status='active',
            account=self.account,
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
            vin='VIN002',
        )

    def test_lease_request_requires_login(self):
        """Создание заявки без логина — редирект."""
        self.client = Client()  # не залогинен
        response = self.client.post(
            reverse('core:leasing_request_create', args=[self.equipment.id]),
            {'message': ''},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_lease_request_creates_record(self):
        """Создание заявки — запись в БД."""
        response = self.client.post(
            reverse('core:leasing_request_create', args=[self.equipment.id]),
            {'message': 'Хочу в лизинг'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            LeaseRequest.objects.filter(
                equipment=self.equipment,
                account=self.account,
            ).exists(),
        )


class ChatAccessTest(TestCase):
    """Интеграционный тест: доступ к чату."""

    def setUp(self):
        self.client = Client()
        self.account = _login_as_client(self.client)
        self.category = EquipmentCategory.objects.create(name='Тракторы')
        self.manufacturer = Manufacturer.objects.create(name='Deere')
        self.equipment = Equipment.objects.create(
            name='Трактор',
            model='8R',
            category=self.category,
            manufacturer=self.manufacturer,
            price=Decimal('10000000'),
            status='available',
            vin='VIN003',
        )
        self.lease_request = LeaseRequest.objects.create(
            equipment=self.equipment,
            account=self.account,
            status='pending',
        )

    def test_chat_requires_login(self):
        """Чат без логина — редирект."""
        self.client = Client()
        response = self.client.get(reverse('chat:thread', args=[self.lease_request.id]))
        self.assertEqual(response.status_code, 302)

    def test_chat_accessible_by_request_owner(self):
        """Чат доступен владельцу заявки."""
        response = self.client.get(reverse('chat:thread', args=[self.lease_request.id]))
        self.assertEqual(response.status_code, 200)
