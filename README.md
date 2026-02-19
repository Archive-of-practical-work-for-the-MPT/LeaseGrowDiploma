# LeaseGrow

Django-проект для лизинга агротехники.

## Структура проекта

```
LeaseGrow/
├── manage.py
├── config/                      # Конфигурация проекта
│   ├── settings/
│   │   ├── base.py              # Базовые настройки
│   │   ├── local.py             # Разработка
│   │   └── production.py        # Продакшен
│   ├── urls.py
│   ├── api_urls.py              # Объединённый API
│   └── wsgi.py
├── apps/                        # Приложения (шаблоны в apps/*/templates/)
│   ├── accounts/                # Пользователи, роли, профили, токены API
│   ├── catalog/                 # Каталог техники (категории, производители, техника)
│   ├── leasing/                 # Компании, договоры, платежи, обслуживание
│   └── core/                    # Главная страница, аудит, общие компоненты
├── static/
├── media/
└── requirements.txt
```

## Установка

```bash
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## Настройка окружения

1. Скопируйте `.env.example` в `.env` и заполните переменные:
   - **SECRET_KEY** — сгенерируйте:  
     `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
   - **DB_PASSWORD** — пароль пользователя PostgreSQL

2. Создайте и заполните базу данных одной командой:
   ```bash
   python scripts/run_db_setup.py
   ```
   Скрипт читает параметры из `.env`, создаёт БД, схему и заполняет тестовыми данными.  
   **Админ:** `admin@gmail.com` / `adminadmin`

3. Примените миграции Django (схема уже создана скриптом):
   ```bash
   python manage.py migrate --fake-initial
   ```

## Запуск

```bash
# Если БД пустая и создаёте через Django:
python manage.py migrate

# Запуск сервера
python manage.py runserver
```

Сайт: http://127.0.0.1:8000/

## API

API построен по таблицам БД — CRUD (list, create, retrieve, update, destroy).

Корень: **http://127.0.0.1:8000/api/**

Ресурсы: `roles`, `accounts`, `user_profiles`, `account_tokens`, `companies`, `company_contacts`, `equipment_categories`, `manufacturers`, `equipment`, `lease_contracts`, `payment_schedules`, `maintenances`, `maintenance_requests`, `audit_logs`.

**Авторизация через API:**
- Вход: `POST /api/account-tokens/` с телом `{"username": "логин или email", "password": "пароль"}` — в ответе создаётся токен (поле `key`).
- В заголовке запросов: `Authorization: Token <key>`.
- Выход: `DELETE /api/account-tokens/<id>/` (удаление своего токена).
- Регистрация: `POST /api/accounts/` (при создании передать `password`), затем `POST /api/user-profiles/`.
