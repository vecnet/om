# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-30 11:32


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ts_om', '0001_scenario_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simulation',
            name='last_error_message',
            field=models.TextField(blank=True, default=b''),
        ),
    ]
