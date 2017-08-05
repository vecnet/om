# -*- coding: utf-8 -*-
#
# This file is part of the VecNet OpenMalaria Portal.
# For copyright and licensing information about this package, see the
# NOTICE.txt and LICENSE.txt files in its top-level directory; they are
# available at https://github.com/vecnet/om
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0.  If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.contrib.auth.models import User
from django.test.testcases import TestCase
from mock.mock import patch

from website.apps.ts_om.models import Scenario, Simulation
from website.apps.ts_om.submit import submit

class MockPopen:
    pid = 1234

class SubmitNewTest(TestCase):
    @patch("sim_services_local.dispatcher.subprocess.Popen")
    def test_success(self, subprocess_func):
        subprocess_func.return_value = MockPopen()
        user = User.objects.create(username="user")
        scenario = Scenario.objects.create(xml="123", user=user)
        simulation = submit(scenario)
        scenario.refresh_from_db()
        self.assertEqual(scenario.new_simulation, simulation)
        self.assertEqual(scenario.new_simulation.pid, "1234")
        self.assertEqual(scenario.new_simulation.status, Simulation.QUEUED)
        self.assertEqual(scenario.new_simulation.input_file.read(), "123")
        self.assertEqual(scenario.new_simulation.last_error_message, "")\

    @patch("sim_services_local.dispatcher.subprocess.Popen")
    def test_runtime_error(self, subprocess_func):
        subprocess_func.side_effect = RuntimeError()
        user = User.objects.create(username="user")
        scenario = Scenario.objects.create(xml="123", user=user)
        simulation = submit(scenario)
        scenario.refresh_from_db()
        self.assertEqual(scenario.new_simulation, None)
        self.assertEqual(simulation, None)

    @patch("sim_services_local.dispatcher.subprocess.Popen")
    def test_double_submit(self, subprocess_func):
        subprocess_func.return_value = MockPopen()
        user = User.objects.create(username="user")
        scenario = Scenario.objects.create(xml="123", user=user)
        simulation = submit(scenario)
        scenario.refresh_from_db()
        self.assertEqual(scenario.new_simulation, simulation)
        self.assertEqual(scenario.new_simulation.pid, "1234")
        self.assertEqual(scenario.new_simulation.status, Simulation.QUEUED)
        self.assertEqual(scenario.new_simulation.input_file.read(), "123")
        self.assertEqual(scenario.new_simulation.last_error_message, "")

        simulation = submit(scenario)
        self.assertEqual(simulation, None)

    @patch("sim_services_local.dispatcher.subprocess.Popen")
    def test_ioerror(self, subprocess_func):
        subprocess_func.side_effect = IOError("IO Error")
        user = User.objects.create(username="user")
        scenario = Scenario.objects.create(xml="123", user=user)
        simulation = submit(scenario)
        scenario.refresh_from_db()
        self.assertEqual(scenario.new_simulation, simulation)
        self.assertEqual(scenario.new_simulation.pid, "")
        self.assertEqual(scenario.new_simulation.status, Simulation.FAILED)
        self.assertEqual(scenario.new_simulation.input_file.read(), "123")
        self.assertEqual(scenario.new_simulation.last_error_message, "Subprocess failed: IO Error")
