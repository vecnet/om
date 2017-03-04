# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

import website.apps.ts_om.utils

def migrate_simulations(apps, schema_editor):
    website.apps.ts_om.utils.migrate_simulations()


class Migration(migrations.Migration):

    dependencies = [
        ('ts_om', '0003_auto_20170303_1758'),
    ]

    operations = [
        migrations.RunPython(migrate_simulations),
    ]
