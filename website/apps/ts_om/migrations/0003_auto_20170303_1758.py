# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ts_om', '0002_auto_20170302_1920'),
    ]

    operations = [
        migrations.CreateModel(
            name='Simulation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.TextField(default=b'32')),
                ('status', models.TextField(default=b'New', choices=[(b'New', b'New'), (b'Submitted', b'Submitted'), (b'Running', b'Running'), (b'Complete', b'Complete'), (b'Failed', b'Failed')])),
                ('pid', models.TextField(default=b'')),
                ('cwd', models.TextField(default=b'')),
                ('input_file', models.FileField(null=True, upload_to=b'files/%Y/%m/', blank=True)),
                ('output_file', models.FileField(null=True, upload_to=b'files/%Y/%m/', blank=True)),
                ('ctsout_file', models.FileField(null=True, upload_to=b'files/%Y/%m/', blank=True)),
                ('model_stdout', models.FileField(null=True, upload_to=b'files/%Y/%m/', blank=True)),
                ('creation_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('last_error_message', models.TextField(default=b'')),
            ],
            options={
                'db_table': 'simulation',
            },
        ),
        migrations.AddField(
            model_name='scenario',
            name='new_simulation',
            field=models.OneToOneField(related_name='scenario', null=True, blank=True, to='ts_om.Simulation'),
        ),
    ]
