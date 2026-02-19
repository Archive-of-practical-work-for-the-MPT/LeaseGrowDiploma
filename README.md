# LeaseGrow

Django-проект для лизинга агротехники.

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
   Скрипт читает параметры из `.env` (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT), создаёт БД (если нет), схему и заполняет тестовыми данными.  
   **Админ:** `admin@gmail.com` / `adminadmin`  
   При необходимости можно выполнить SQL вручную: `scripts/create_db.sql` — схема, `scripts/seed_db.sql` — данные.  
   После скрипта выполните `python manage.py migrate --fake`, чтобы Django зафиксировал миграции (схема уже создана).

## Запуск

```bash
# Если БД создавали через run_db_setup.py:
python manage.py migrate --fake

# Если БД пустая и создаёте через Django:
python manage.py migrate

python manage.py runserver
```

Сайт: http://127.0.0.1:8000/

## API

API построен только по таблицам БД — у каждого ресурса все поля модели, CRUD (list, create, retrieve, update, destroy).

Корень: **http://127.0.0.1:8000/api/**

Ресурсы: `roles`, `accounts`, `user_profiles`, `account_tokens`, `companies`, `company_contacts`, `equipment_categories`, `manufacturers`, `equipment`, `lease_contracts`, `payment_schedules`, `maintenances`, `maintenance_requests`, `audit_logs`.

**Авторизация через API таблиц:**
- Вход: `POST /api/account-tokens/` с телом `{"username": "логин или email", "password": "пароль"}` — в ответе создаётся запись токена (поле `key`).
- Дальше в заголовке запросов: `Authorization: Token <key>`.
- Выход: `DELETE /api/account-tokens/<id>/` (удаление своего токена).
- Регистрация: `POST /api/accounts/` (поля таблицы account, при создании передать `password`), затем `POST /api/user-profiles/` (привязать профиль к account).
