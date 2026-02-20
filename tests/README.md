# Тесты LeaseGrow

Тестирование через встроенный в Django тест-раннер с подробным выводом на русском.

## Кастомный тест-раннер

В `config/settings/base.py` задан `TEST_RUNNER = 'tests.test_runner.RussianDiscoverRunner'`. При запуске тестов выводятся:
- заголовок «LeaseGrow — автоматизированные тесты»;
- нумерованный список тестов с русскими описаниями;
- статус каждого теста: «пройден», «ПРОВАЛ», «ОШИБКА»;
- итоговая строка: «Выполнено тестов: N, все пройдены успешно» или «провалов/ошибок: N».

## Запуск

Из папки LeaseGrow (где лежит `manage.py`):

```bash
# Все тесты пакета tests
python manage.py test tests

# Только CRUD
python manage.py test tests.test_crud

# Только API
python manage.py test tests.test_api

# Только экспорт
python manage.py test tests.test_export

# Только веб-страницы
python manage.py test tests.test_views
```

## Структура тестов

| Модуль | Описание |
|--------|----------|
| `test_crud.py` | Функциональные тесты: CRUD для Role, Account, Equipment, LeaseRequest |
| `test_api.py` | Интеграционные тесты: REST API (техника, компании, аутентификация) |
| `test_export.py` | Интеграционные тесты: экспорт статистики (Excel, PDF) для менеджера |
| `test_views.py` | Интеграционные тесты: веб-страницы (главная, логин, профиль, лизинг, чат) |
| `locustfile.py` | Нагрузочное тестирование API и страниц |
