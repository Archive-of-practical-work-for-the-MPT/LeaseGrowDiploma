# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0007_company_rename_legal_fields'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CompanyContact',
        ),
    ]
