# Дипломный проект "LeaseGrow" - веб-приложение для лизинга сельскохозяйственной техники.

## О проекте

LeaseGrow - это современное веб-приложение для лизинга сельскохозяйственной техники. Клиенты оставляют заявки, менеджеры подтверждают их и оформляют договоры, ведется учет платежей и заявок на обслуживание.

## Демонстрация

<p align="center">
      <img src="https://github.com/user-attachments/assets/be0053f1-30cf-4245-a81d-d3f6c70b63b4" alt="Демонстрация" width="700">
</p>

<p align="center">
      <img src="https://github.com/user-attachments/assets/c4e3ff86-9fc1-4692-8449-d0a014dd4dc3" alt="Демонстрация" width="700">
</p>

## Брендбук

<p align="center">
      <img src="https://github.com/user-attachments/assets/3fc55b90-0967-4b9c-816e-8de073f8cf48" alt="Брендбук" width="550">
</p>

## Требования
<details>
<summary>Нажмите чтобы расскрыть</summary>
Дата, до которой нужно загрузить КП у каждой группы своя, согласовывается с преподавателем.

Титульный лист ПЗ  в эл. виде, без подписей.
Бланк задания в эл. виде, без подписей.

Курсовой проект сдаем  в электронном виде (не печатать). 
Для сдачи нужно загрузить все элементы КП в следующем виде:

1. Файл в формате .pdf собранный в следующей последовательности:
титульный лист 
бланк задания на КП (2 страницы)
ПЗ с приложениями
"Антиплагиат" с сайта Антиплагиат.ру
Имя файла 09.02.07 группа ФИО КП МДК 02.01 ТРПО (09.02.07 П50-1-22 Иванов И.И. КП  МДК 02.01 ТРПО.pdf)
</details>

## Технологии
- Python 3.13+
- Django 5.2
- PostgreSQL 18+
- Django REST Framework
- HTML5, CSS3
- Locust

### Структура проекта
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

### Роли пользователей

| Роль | Описание | Доступ |
|------|----------|--------|
| admin | Администратор системы | Полный доступ: панель управления (CRUD по всем таблицам), журнал аудита, раздел менеджера, Django Admin |
| manager | Менеджер лизинга | Каталог заявок, чаты с клиентами, оформление договоров, статистика, экспорт Excel/PDF, панель управления (ограниченный набор таблиц) |
| client | Клиент (арендатор) | Каталог техники, оформление заявок, чат с менеджером, профиль, моя техника, заявки на обслуживание |

## Как запустить проект?

### Требования
- Python >3.13
- PostgreSQL >16 (установлен и запущен)
- Учётная запись с правами на создание БД (обычно `postgres`)

### Шаги

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

- Нагрузочное тестирование: см. `tests/locust/README.md`
- Панель управления: `/control-panel/` (только admin, частично manager)
- Журнал аудита: логирует INSERT/UPDATE/DELETE в панели управления
