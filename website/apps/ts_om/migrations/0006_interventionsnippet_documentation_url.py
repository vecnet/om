# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ts_om', '0005_remove_scenario_simulation'),
    ]

    operations = [
        migrations.AddField(
            model_name='interventionsnippet',
            name='documentation_url',
            field=models.TextField(blank=True),
        ),
    ]
