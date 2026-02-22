# LeaseGrow

Веб-приложение для лизинга сельскохозяйственной техники. Клиенты оставляют заявки, менеджеры подтверждают их и оформляют договоры, ведется учет платежей и заявок на обслуживание.

## Стек технологий

- Python 3.11+
- Django 5.2
- PostgreSQL 16+
- Django REST Framework
- Channels, Daphne (ASGI, WebSocket)
- Whitenoise (статика)
- OpenPyXL, ReportLab, Matplotlib (отчеты, экспорт)
- Locust (нагрузочное тестирование)

## Роли пользователей

| Роль | Описание | Доступ |
|------|----------|--------|
| admin | Администратор системы | Полный доступ: панель управления (CRUD по всем таблицам), журнал аудита, раздел менеджера, Django Admin |
| manager | Менеджер лизинга | Каталог заявок, чаты с клиентами, оформление договоров, статистика, экспорт Excel/PDF, панель управления (ограниченный набор таблиц) |
| accountant | Бухгалтер | Контракты, платежи |
| client | Клиент (арендатор) | Каталог техники, оформление заявок, чат с менеджером, профиль, моя техника, заявки на обслуживание |

## Разделы сайта

**Публичные:**
- Главная (`/`)
- Каталог лизинга (`/leasing/`) — техника, фильтры, оформление заявки
- Вход (`/login/`), регистрация (`/register/`)
- Конфиденциальность (`/privacy/`), О проекте (`/about/`)

**Клиент (после входа):**
- Профиль (`/profile/`) — данные компании, контакты
- Моя техника (`/my-equipment/`) — договоры и подтвержденные заявки
- Заявки на обслуживание (`/my-maintenance/`)
- Чат по заявке (`/chat/<id>/`)

**Менеджер и администратор:**
- Раздел менеджера (`/manager/`) — статистика, чаты, оформление договоров
- Экспорт Excel/PDF (`/manager/statistics/export/`)
- Панель управления (`/control-panel/`) — CRUD по таблицам БД

**Система:**
- REST API (`/api/`) — техника, компании, договоры и др.
- Django Admin (`/admin/`)

## Структура проекта

```
LeaseGrow/
├── manage.py
├── config/                  # Конфигурация
│   ├── settings/            # base, local, production, docker
│   ├── urls.py
│   └── api_urls.py
├── apps/
│   ├── accounts/            # Роли, аккаунты, профили, токены API
│   ├── catalog/             # Категории, производители, техника
│   ├── leasing/             # Компании, договоры, платежи, заявки, чаты
│   ├── core/                # Главная, лизинг, аудит
│   ├── control_panel/       # CRUD-панель для админа/менеджера
│   └── manager/             # Интерфейс менеджера
├── scripts/
│   ├── run_db_setup.py      # Создание БД и seed
│   ├── create_db.sql
│   └── seed_db.sql
├── tests/
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Запуск без Docker

### 1. Установка зависимостей

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

### 2. Настройка окружения

Скопируйте `.env.example` в `.env` и заполните:

- **SECRET_KEY** — сгенерируйте:  
  `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- **DB_NAME** — имя БД (например, leasegrow)
- **DB_USER**, **DB_PASSWORD**, **DB_HOST**, **DB_PORT** — параметры PostgreSQL

### 3. База данных

**Вариант A — скрипт (схема + тестовые данные):**

```bash
python scripts/run_db_setup.py
python manage.py migrate --fake-initial
```

**Вариант B — только Django:**

```bash
python manage.py migrate
```

### 4. Запуск сервера

```bash
python manage.py runserver
```

Сайт: http://127.0.0.1:8000/

**Тестовый админ (после seed):** admin@gmail.com / adminadmin

---

## Запуск с Docker

### Требования

- Docker и Docker Compose

### Шаги

1. Скопируйте `.env.example` в `.env` и заполните (DB_PASSWORD, SECRET_KEY и т.д.).

2. Запустите:

```bash
docker compose up --build
```

3. Сайт: http://localhost:8000

4. Загрузка тестовых данных (после первого запуска):

```bash
docker compose exec -T db psql -U postgres -d leasegrow < scripts/seed_db.sql
```

---

## Запуск тестов

### Требования

- Установленные зависимости (daphne, channels)
- Доступная БД (создается тестовая автоматически)

### Команда

```bash
python manage.py test tests
```

Или по модулям:

```bash
python manage.py test tests.test_crud
python manage.py test tests.test_views
python manage.py test tests.test_api
python manage.py test tests.test_export
```

### Без daphne/channels

Если daphne не установлен, используйте тестовые настройки:

```bash
set DJANGO_SETTINGS_MODULE=config.settings.test
python manage.py test tests
```

---

## REST API

Корень: http://127.0.0.1:8000/api/

Ресурсы: roles, accounts, user-profiles, account-tokens, companies, equipment-categories, manufacturers, equipment, lease-contracts, payment-schedules, maintenance-requests, audit-logs.

**Авторизация:**
- Создание токена: `POST /api/account-tokens/` с телом `{"username": "логин или email", "password": "пароль"}`
- Заголовок: `Authorization: Token <key>`

---

## Дополнительно

- Нагрузочное тестирование: см. `tests/locust/README.md`
- Панель управления: `/control-panel/` (только admin, частично manager)
- Журнал аудита: логирует INSERT/UPDATE/DELETE в панели управления
