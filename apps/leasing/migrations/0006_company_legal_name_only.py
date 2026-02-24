# Generated manually

from django.db import migrations, models


def migrate_company_name_to_legal_name(apps, schema_editor):
    """Копирует name в legal_name, если legal_name пуст."""
    Company = apps.get_model('leasing', 'Company')
    for c in Company.objects.filter(legal_name=''):
        c.legal_name = c.name or 'Без названия'
        c.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0005_maintenance_chat_message'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RemoveField(
                    model_name='company',
                    name='actual_address',
                ),
                migrations.RemoveField(
                    model_name='company',
                    name='kpp',
                ),
                migrations.RemoveField(
                    model_name='company',
                    name='name',
                ),
                migrations.AlterField(
                    model_name='company',
                    name='legal_name',
                    field=models.CharField(max_length=500),
                ),
            ],
        ),
    ]
