# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.core.management import call_command


def site_id(apps, schema_editor):
    call_command('loaddata', 'sites.json')

class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
        ('sites', '0001_initial')
    ]

    operations = [
            migrations.RunPython(site_id)
    ]
