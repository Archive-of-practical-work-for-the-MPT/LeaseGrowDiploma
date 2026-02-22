# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0006_company_legal_name_only'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='legal_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='legal_address',
            new_name='address',
        ),
    ]
