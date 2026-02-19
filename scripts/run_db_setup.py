#!/usr/bin/env python3
"""
Скрипт создания и заполнения БД LeaseGrow (PostgreSQL).
Последовательно выполняет create_db.sql и seed_db.sql.
Устойчив к ошибкам: логирование, проверки, корректные коды выхода.
"""
import os
import sys
from pathlib import Path

# Загрузка .env вручную (без Django)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_FILE = _PROJECT_ROOT / '.env'

if _ENV_FILE.exists():
    for line in _ENV_FILE.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, _, value = line.partition('=')
            value = value.strip().strip('"').strip("'")
            os.environ[key.strip()] = value

# Параметры БД из окружения
DB_NAME = os.environ.get('DB_NAME', 'leasegrow')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')

_SCRIPTS_DIR = Path(__file__).resolve().parent
_CREATE_SQL = _SCRIPTS_DIR / 'create_db.sql'
_SEED_SQL = _SCRIPTS_DIR / 'seed_db.sql'


def log(msg: str, level: str = 'INFO') -> None:
    print(f'[{level}] {msg}', file=sys.stderr if level == 'ERROR' else sys.stdout)


def load_sql(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f'Файл не найден: {path}')
    return path.read_text(encoding='utf-8')


def run_sql(conn, sql: str, description: str) -> bool:
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        log(f'{description}: OK')
        return True
    except Exception as e:
        conn.rollback()
        log(f'{description}: ОШИБКА — {e}', level='ERROR')
        return False


def main() -> int:
    try:
        import psycopg2
        from psycopg2 import sql
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    except ImportError:
        log('Установите psycopg2: pip install psycopg2-binary', level='ERROR')
        return 1

    log('Запуск настройки БД LeaseGrow')
    log(f'Хост: {DB_HOST}:{DB_PORT}, БД: {DB_NAME}, Пользователь: {DB_USER}')

    # 1. Подключение к postgres для создания БД
    try:
        conn_default = psycopg2.connect(
            dbname='postgres',
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        conn_default.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    except Exception as e:
        log(f'Не удалось подключиться к PostgreSQL: {e}', level='ERROR')
        log('Проверьте: сервер запущен, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD в .env', level='ERROR')
        return 1

    # 2. Создание БД, если не существует
    try:
        with conn_default.cursor() as cur:
            cur.execute(
                sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"),
                [DB_NAME]
            )
            if cur.fetchone() is None:
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
                log(f'База данных {DB_NAME} создана')
            else:
                log(f'База данных {DB_NAME} уже существует')
    except Exception as e:
        log(f'Ошибка при создании БД: {e}', level='ERROR')
        conn_default.close()
        return 1

    conn_default.close()

    # 3. Подключение к целевой БД
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
    except Exception as e:
        log(f'Не удалось подключиться к БД {DB_NAME}: {e}', level='ERROR')
        return 1

    success = True

    # 4. Выполнение create_db.sql
    try:
        create_sql = load_sql(_CREATE_SQL)
        if not run_sql(conn, create_sql, 'create_db.sql'):
            success = False
    except FileNotFoundError as e:
        log(str(e), level='ERROR')
        conn.close()
        return 1

    # 5. Проверка: заполнена ли БД тестовыми данными
    seed_needed = True
    if success:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM role WHERE name = %s LIMIT 1",
                    ('admin',)
                )
                if cur.fetchone() is not None:
                    seed_needed = False
                    log('БД уже заполнена тестовыми данными. seed_db.sql пропускается.')
        except Exception:
            pass  # таблица role может не существовать — тогда выполняем seed

    # 6. Выполнение seed_db.sql (если данные ещё не загружены)
    if success and seed_needed:
        try:
            seed_sql = load_sql(_SEED_SQL)
            if not run_sql(conn, seed_sql, 'seed_db.sql'):
                success = False
        except FileNotFoundError as e:
            log(str(e), level='ERROR')
            success = False

    conn.close()

    if success:
        log('Настройка БД завершена успешно.')
        log(f'Админ: admin@gmail.com / adminadmin')
        return 0
    else:
        log('Настройка завершена с ошибками.', level='ERROR')
        return 1


if __name__ == '__main__':
    sys.exit(main())
