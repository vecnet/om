# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.core.management import call_command


def initial_data(apps, schema_editor):
    # call_command('loaddata', 'standard_groups.json')
    pass


class Migration(migrations.Migration):
    # Load fixture file with standard groups
    # Note this migration should be called after table for groups has been created,
    # thus dependency on auth application

    dependencies = [
        ("auth", "0006_require_contenttypes_0002")
    ]

    operations = [
        migrations.RunPython(initial_data)
    ]
