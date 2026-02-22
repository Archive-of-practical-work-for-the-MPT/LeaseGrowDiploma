# Generated manually

import json

from django.db import migrations, models


def json_to_text(apps, schema_editor):
    """Преобразует JSON-значения specifications в читаемый текст."""
    Equipment = apps.get_model('catalog', 'Equipment')
    for eq in Equipment.objects.all():
        val = eq.specifications
        text = ''
        if isinstance(val, dict) and val:
            parts = [f'{k}: {v}' for k, v in val.items()]
            text = ', '.join(parts)
        elif isinstance(val, str) and val.strip():
            if val.strip().startswith('{'):
                try:
                    d = json.loads(val)
                    if d:
                        parts = [f'{k}: {v}' for k, v in d.items()]
                        text = ', '.join(parts)
                    else:
                        text = val
                except json.JSONDecodeError:
                    text = val
            else:
                text = val
        eq.specifications_new = text
        eq.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='specifications_new',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.RunPython(json_to_text, noop),
        migrations.RemoveField(
            model_name='equipment',
            name='specifications',
        ),
        migrations.RenameField(
            model_name='equipment',
            old_name='specifications_new',
            new_name='specifications',
        ),
    ]
