# Нагрузочное тестирование Locust (LeaseGrow)

## Установка

```bash
pip install locust
```

## Подготовка

1. Запустите сервер Django:
   ```bash
   python manage.py runserver
   ```

2. (Опционально) Для `LoggedInWebsiteUser` используйте аккаунт из seed:
   - email: `admin@gmail.com`
   - пароль: `adminadmin`

## Запуск

### С конфигом

Из папки LeaseGrow:

```bash
locust -f tests/locust/locustfile.py --config tests/locust/locust.conf
```

### Без конфига

```bash
locust -f tests/locust/locustfile.py --host http://localhost:8000
```

### Без веб-интерфейса (headless)

```bash
locust -f tests/locust/locustfile.py --host http://localhost:8000 --headless -u 50 -r 5 -t 60s
```

## Веб-интерфейс

Откройте в браузере: **http://localhost:8089**

- **Number of users** — число виртуальных пользователей
- **Spawn rate** — скорость добавления пользователей в секунду
- **User classes** — выбор типа пользователей (WebsiteUser, ApiUser, LoggedInWebsiteUser)
- Нажмите **Start swarming** для начала теста

## Типы пользователей

| Класс | Описание |
|-------|----------|
| **WebsiteUser** | Просмотр публичных страниц: главная, лизинг, вход, конфиденциальность |
| **ApiUser** | REST API (read-only): техника, компании, категории, производители |
| **LoggedInWebsiteUser** | Залогиненный пользователь: главная, лизинг, профиль |

## Структура

```
tests/locust/
├── README.md      # этот файл
├── locust.conf    # конфигурация Locust
└── locustfile.py  # определение пользователей и задач
```
