# Copyright (C) 2016, University of Notre Dame
# All rights reserved
from django.contrib.auth.models import User
from django.test.testcases import TestCase
from mock.mock import patch

from website.apps.ts_om.models import Scenario, Simulation
from website.apps.ts_om.submit import submit_new

class MockPopen:
    pid = 1234

class SubmitNewTest(TestCase):
    @patch("sim_services_local.dispatcher.subprocess.Popen")
    def test_success(self, subprocess_func):
        subprocess_func.return_value = MockPopen()
        user = User.objects.create(username="user")
        scenario = Scenario.objects.create(xml="123", user=user)
        simulation = submit_new(scenario)
        scenario.refresh_from_db()
        self.assertEqual(scenario.new_simulation, simulation)
        self.assertEqual(scenario.new_simulation.pid, "1234")
        self.assertEqual(scenario.new_simulation.status, Simulation.QUEUED)
        self.assertEqual(scenario.new_simulation.input_file.read(), "123")
        self.assertEqual(scenario.new_simulation.last_error_message, "")

    @patch("sim_services_local.dispatcher.subprocess.Popen")
    def test_ioerror(self, subprocess_func):
        subprocess_func.side_effect = IOError("IO Error")
        user = User.objects.create(username="user")
        scenario = Scenario.objects.create(xml="123", user=user)
        simulation = submit_new(scenario)
        scenario.refresh_from_db()
        self.assertEqual(scenario.new_simulation, simulation)
        self.assertEqual(scenario.new_simulation.pid, "")
        self.assertEqual(scenario.new_simulation.status, Simulation.FAILED)
        self.assertEqual(scenario.new_simulation.input_file.read(), "123")
        self.assertEqual(scenario.new_simulation.last_error_message, "Subprocess failed: IO Error")
