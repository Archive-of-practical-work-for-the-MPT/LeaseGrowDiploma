"""
Locust: нагрузочное тестирование LeaseGrow.

Два типа пользователей:
- WebsiteUser: просмотр публичных страниц (главная, лизинг, вход, конфиденциальность).
- ApiUser: работа с REST API (техника, компании, категории) — read-only без авторизации.

Запуск с веб-интерфейсом:
  cd LeaseGrow && locust -f tests/locust/locustfile.py --config tests/locust/locust.conf

Или без конфига:
  locust -f tests/locust/locustfile.py --host http://localhost:8000

Затем открыть http://localhost:8089
"""
import re
from locust import HttpUser, task, between


class WebsiteUser(HttpUser):
    """Пользователь, просматривающий публичные страницы сайта."""

    wait_time = between(1, 3)

    @task(4)
    def index(self):
        """Главная страница."""
        self.client.get("/")

    @task(3)
    def leasing(self):
        """Страница каталога лизинга."""
        self.client.get("/leasing/")

    @task(2)
    def login_page(self):
        """Страница входа."""
        self.client.get("/login/")

    @task(1)
    def privacy(self):
        """Страница конфиденциальности."""
        self.client.get("/privacy/")


class ApiUser(HttpUser):
    """
    Пользователь API: выполняет запросы к REST API (read-only).
    Использует публичные read-эндпоинты, авторизация не требуется.
    """

    wait_time = between(0.5, 2)

    @task(4)
    def api_root(self):
        """Корень API."""
        self.client.get("/api/")

    @task(4)
    def api_equipment_list(self):
        """Список техники."""
        self.client.get("/api/equipment/")

    @task(3)
    def api_companies_list(self):
        """Список компаний."""
        self.client.get("/api/companies/")

    @task(2)
    def api_equipment_categories(self):
        """Категории техники."""
        self.client.get("/api/equipment-categories/")

    @task(2)
    def api_manufacturers(self):
        """Производители."""
        self.client.get("/api/manufacturers/")

    @task(1)
    def api_lease_contracts(self):
        """Договоры лизинга (список)."""
        self.client.get("/api/lease-contracts/")


class LoggedInWebsiteUser(HttpUser):
    """
    Пользователь, залогиненный в веб-интерфейсе.
    Требуется аккаунт админа из seed (admin@gmail.com / adminadmin).
    """

    wait_time = between(1, 4)

    def on_start(self):
        """Авторизация при старте виртуального пользователя."""
        self._login()

    def _login(self):
        """Вход в систему для получения сессии."""
        response = self.client.get("/login/")
        if response.status_code != 200:
            return
        csrf = self.client.cookies.get("csrftoken")
        if not csrf:
            match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
            csrf = match.group(1) if match else ""
        self.client.post(
            "/login/",
            {
                "username": "admin@gmail.com",
                "password": "adminadmin",
                "csrfmiddlewaretoken": csrf,
            },
            headers={"Referer": f"{self.host}/login/"},
        )

    @task(3)
    def index(self):
        """Главная после входа."""
        self.client.get("/")

    @task(3)
    def leasing(self):
        """Каталог лизинга."""
        self.client.get("/leasing/")

    @task(2)
    def profile(self):
        """Профиль пользователя."""
        self.client.get("/profile/")
