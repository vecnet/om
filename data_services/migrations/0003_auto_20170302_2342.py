# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_services', '0002_auto_20170302_2333'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='simulationgroup',
            name='submitted_by',
        ),
        migrations.RemoveField(
            model_name='simulationinputfile',
            name='created_by',
        ),
    ]
