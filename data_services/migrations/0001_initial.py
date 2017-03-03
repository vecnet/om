# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DimUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(unique=True, max_length=30)),
                ('first_name', models.CharField(max_length=30, null=True, blank=True)),
                ('last_name', models.CharField(max_length=30, null=True, blank=True)),
                ('organization', models.TextField(null=True, blank=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(null=True)),
            ],
            options={
                'db_table': 'dim_user',
            },
        ),
        migrations.CreateModel(
            name='Simulation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('model', models.CharField(help_text=b'simulation model ID', max_length=4, choices=[(b'EMOD', b'EMOD'), (b'OM', b'OpenMalaria'), (b'mock', b'mock'), (b'ECLB', b'Notre Dame EMOD Calibration tool')])),
                ('version', models.CharField(help_text=b'version of simulation model', max_length=20)),
                ('cmd_line_args', models.CharField(help_text=b'additional command line arguments passed to the model', max_length=100, blank=True)),
                ('status', models.CharField(help_text=b'status of the simulation', max_length=7, choices=[(b'ready', b'ready to run'), (b'start', b'script started'), (b'input', b'staging input files'), (b'model', b'running model'), (b'output', b'processing output files'), (b'out:err', b'error transmitting output'), (b'done', b'script done'), (b'error', b'error occurred')])),
                ('started_when', models.DateTimeField(help_text=b'when was the simulation started', null=True, blank=True)),
                ('duration', models.BigIntegerField(help_text=b'how long the simulation ran (in seconds)', null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='SimulationGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('submitted_when', models.DateTimeField(help_text=b'when was the group submitted', null=True, blank=True)),
                ('submitted_by', models.ForeignKey(help_text=b'who submitted the group for execution', to='data_services.DimUser')),
            ],
        ),
        migrations.CreateModel(
            name='SimulationInputFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(help_text=b"file's name (e.g., 'ctsout.txt', 'config.json')")),
                ('uri', models.TextField(help_text=b"where the file's contents are stored")),
                ('metadata', jsonfield.fields.JSONField(help_text=b'additional info about the file, e.g., its data format')),
                ('created_when', models.DateTimeField(help_text=b'when was the file created', auto_now_add=True)),
                ('created_by', models.ForeignKey(help_text=b'who created the file', to='data_services.DimUser')),
                ('simulations', models.ManyToManyField(help_text=b'the simulations that used this file as input', related_name='input_files', to='data_services.Simulation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SimulationOutputFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(help_text=b"file's name (e.g., 'ctsout.txt', 'config.json')")),
                ('uri', models.TextField(help_text=b"where the file's contents are stored")),
                ('metadata', jsonfield.fields.JSONField(help_text=b'additional info about the file, e.g., its data format')),
                ('simulation', models.ForeignKey(blank=True, to='data_services.Simulation', help_text=b'the simulation that produced this file', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='simulation',
            name='group',
            field=models.ForeignKey(related_name='simulations', to='data_services.SimulationGroup'),
        ),
    ]
