# Generated manually

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0003_add_chat_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='leasecontract',
            name='lease_request',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='lease_contract',
                to='leasing.leaserequest',
            ),
        ),
    ]
