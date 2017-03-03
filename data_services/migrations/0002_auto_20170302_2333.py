# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings

def convert_submitted_by_to_submitted_by_user(apps, schema_editor):
    SimulationGroup = apps.get_model("data_services", "SimulationGroup")
    User = apps.get_model("auth", "User")

    for sim_group in SimulationGroup.objects.all():
         sim_group.submitted_by_user = User.objects.get(username=sim_group.submitted_by.username)

class Migration(migrations.Migration):

    dependencies = [
        ('data_services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='simulationgroup',
            name='submitted_by_user',
            field=models.ForeignKey(related_name='simulation_groups', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(convert_submitted_by_to_submitted_by_user),
    ]
