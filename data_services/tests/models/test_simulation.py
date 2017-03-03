# Copyright (C) 2016, University of Notre Dame
# All rights reserved
import datetime

from django.contrib.auth.models import User
from django.test.testcases import TestCase
from vecnet.simulation import sim_status

from data_services.models import Simulation, SimulationGroup


class SimulationModelTest(TestCase):
    def setUp(self):
        self.sim_group = SimulationGroup.objects.create(
            submitted_by_user=User.objects.create(username="user")
        )
        self.simulation = Simulation.objects.create(
            group=self.sim_group,
            model="123",
            version="v30",
            status="DONE"
        )

    def test_duration_as_timedelta_none(self):
        self.simulation.duration = None  # seconds
        self.assertEqual(self.simulation.duration_as_timedelta, None)

    def test_duration_as_timedelta(self):
        self.simulation.duration = 30  # seconds
        self.assertEqual(self.simulation.duration_as_timedelta, datetime.timedelta(seconds=30))

    def test_ended_when(self):
        self.simulation.started_when = datetime.datetime(1990, 12, 12)
        self.simulation.duration = 30  # seconds
        self.assertEqual(self.simulation.ended_when, datetime.datetime(1990, 12, 12, second=30))

    def test_str(self):
        simulation_as_string = "{} (123 vv30) - DONE".format(self.simulation.id)
        self.assertEqual(str(self.simulation), simulation_as_string)

    def test_copy(self):
        new_simulation = self.simulation.copy()
        self.assertNotEqual(new_simulation.group, self.simulation.group)
        self.assertNotEqual(new_simulation.id, self.simulation.id)
        self.assertEqual(new_simulation.status, sim_status.READY_TO_RUN)
