# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-12 19:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='email',
            name='status',
            field=models.CharField(choices=[(b'Unsent', b'Unsent'), (b'Failed', b'Failed'), (b'Sent', b'Sent')], default=b'Unsent', max_length=30),
        ),
    ]
