# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RemoveField(
                    model_name='auditlog',
                    name='ip_address',
                ),
                migrations.RemoveField(
                    model_name='auditlog',
                    name='user_agent',
                ),
            ],
        ),
    ]
