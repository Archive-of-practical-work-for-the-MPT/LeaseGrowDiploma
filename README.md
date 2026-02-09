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

2. Создайте базу данных в PostgreSQL:
   ```sql
   CREATE DATABASE greenquality;
   ```

## Запуск

```bash
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
