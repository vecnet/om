# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('data_services', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AnophelesSnippet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('anopheles', models.TextField()),
                ('gvi_anophelesParams', models.TextField(null=True, blank=True)),
                ('itn_anophelesParams', models.TextField(null=True, blank=True)),
                ('irs_anophelesParams', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='BaselineScenario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('xml', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='DemographicsSnippet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('maximum_age_yrs', models.CharField(max_length=200)),
                ('xml', models.TextField()),
                ('title', models.CharField(max_length=200)),
                ('url', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('description', models.TextField(default=b'', blank=True)),
                ('experiment_specification', models.TextField(null=True, blank=True)),
                ('sim_group', models.ForeignKey(blank=True, to='data_services.SimulationGroup', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExperimentFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('file', models.FileField(upload_to=b'ts_om/experiments/%Y/%m/%d')),
                ('sim_group', models.ForeignKey(related_name='submit_group', to='data_services.SimulationGroup', null=True)),
                ('test_sim_group', models.ForeignKey(related_name='test_submit_group', to='data_services.SimulationGroup', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='InterventionComponent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('tag', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='InterventionSnippet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('xml', models.TextField()),
                ('component', models.ForeignKey(to='ts_om.InterventionComponent', on_delete=django.db.models.deletion.PROTECT), ),
            ],
        ),
        migrations.CreateModel(
            name='ModelSnippet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('xml', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Scenario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('xml', models.TextField()),
                ('start_date', models.IntegerField(default=2016)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('description', models.TextField(null=True, blank=True)),
                ('is_public', models.BooleanField(default=False)),
                ('baseline', models.ForeignKey(blank=True, to='ts_om.BaselineScenario', null=True, on_delete=django.db.models.deletion.PROTECT)),
                ('simulation', models.ForeignKey(blank=True, to='data_services.Simulation', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='SweepArmMappingToScenario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sweep_name', models.CharField(max_length=127)),
                ('arm_name', models.CharField(max_length=127)),
                ('experiment', models.ForeignKey(to='ts_om.Experiment')),
                ('scenario', models.ForeignKey(to='ts_om.Scenario')),
            ],
        ),
    ]
