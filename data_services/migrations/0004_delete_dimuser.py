# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_services', '0003_auto_20170302_2342'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DimUser',
        ),
    ]
