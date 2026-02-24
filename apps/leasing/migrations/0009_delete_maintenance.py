# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0008_delete_companycontact'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(
                    name='Maintenance',
                ),
            ],
        ),
    ]
