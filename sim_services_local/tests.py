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
from django.test.testcases import TestCase
from django.test.utils import override_settings
from mock.mock import patch

from sim_services_local.dispatcher import submit
from website.apps.ts_om.models import Simulation


class DispatcherTest(TestCase):
    @override_settings(PYTHON_EXECUTABLE="python_")
    @patch("sim_services_local.dispatcher.subprocess.Popen")
    def test_python_executable(self, popen_func):
        simulation = Simulation.objects.create()
        popen_func.side_effect = IOError("Test error")
        result = submit(simulation)
        self.assertEqual(result, None)
        self.assertEqual(popen_func.called, True)
        args, kwargs = popen_func.call_args
        self.assertEqual(args[0][0], "python_")
        simulation.refresh_from_db()
        self.assertEqual(simulation.status, Simulation.FAILED)
        self.assertEqual(simulation.last_error_message, "Subprocess failed: Test error")
