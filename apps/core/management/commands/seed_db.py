from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from apps.accounts.models import Role


class Command(BaseCommand):
    help = 'Загружает тестовые данные из scripts/seed_db.sql, если база ещё пустая.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Загрузить seed SQL даже если тестовые данные уже есть.',
        )

    def handle(self, *args, **options):
        seed_path = Path(settings.BASE_DIR) / 'scripts' / 'seed_db.sql'

        if not seed_path.exists():
            raise CommandError(f'Файл с тестовыми данными не найден: {seed_path}')

        if Role.objects.exists() and not options['force']:
            self.stdout.write(self.style.WARNING('Тестовые данные уже есть, загрузка пропущена.'))
            return

        seed_sql = seed_path.read_text(encoding='utf-8')

        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(seed_sql)
        except Exception as exc:
            raise CommandError(f'Не удалось загрузить тестовые данные: {exc}') from exc

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно загружены.'))
