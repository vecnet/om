# -*- coding: utf-8 -*-


from django.core.management import call_command
from django.db import migrations, models


def load_fixtures(apps, schema_editor):
    call_command('loaddata', 'AnophelesSnippets.json')
    call_command('loaddata', 'BaselineScenarios.json')
    call_command('loaddata', 'DemographicsSnippets.json')
    call_command('loaddata', 'Interventions.json')

class Migration(migrations.Migration):

    dependencies = [
        ('ts_om', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixtures),
    ]
