"""
Интеграционные тесты: экспорт статистики менеджера (Excel, PDF).
Запуск: из папки LeaseGrow выполнить
  python manage.py test tests.test_export
"""
from django.contrib.auth.hashers import make_password
from django.test import TestCase, Client
from django.urls import reverse

from apps.accounts.models import Account, Role, UserProfile


def _login_as_manager(client):
    """Создаёт роль менеджера, аккаунт и авторизует сессию."""
    role = Role.objects.create(
        name='manager',
        description='Менеджер',
        permissions=['contracts', 'companies'],
    )
    account = Account.objects.create(
        email='manager@test.local',
        username='manager',
        password_hash=make_password('managerpass'),
        role=role,
    )
    UserProfile.objects.create(account=account, first_name='Менеджер', last_name='Тест')
    session = client.session
    session['account_id'] = account.id
    session.save()
    return account


class ExportStatisticsTest(TestCase):
    """Интеграционный тест: экспорт статистики для менеджера (Excel и PDF)."""

    def setUp(self):
        self.client = Client()

    def test_export_without_login_redirects(self):
        """Экспорт без авторизации — редирект на логин."""
        url_excel = reverse('manager:statistics_export_excel')
        response = self.client.get(url_excel)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

        url_pdf = reverse('manager:statistics_export_pdf')
        response = self.client.get(url_pdf)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_export_excel_as_manager(self):
        """Экспорт Excel: под менеджером — 200, content-type spreadsheet."""
        _login_as_manager(self.client)
        url = reverse('manager:statistics_export_excel')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content_type = response.get('Content-Type', '')
        self.assertIn('spreadsheet', content_type)

    def test_export_pdf_as_manager(self):
        """Экспорт PDF: под менеджером — 200, content-type pdf."""
        _login_as_manager(self.client)
        url = reverse('manager:statistics_export_pdf')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content_type = response.get('Content-Type', '')
        self.assertIn('pdf', content_type)
