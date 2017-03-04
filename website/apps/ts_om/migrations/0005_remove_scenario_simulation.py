# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ts_om', '0004_auto_20170303_2153'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scenario',
            name='simulation',
        ),
    ]
