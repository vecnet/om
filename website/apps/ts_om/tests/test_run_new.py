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

import os
from django.test.testcases import TestCase
from django.conf import settings

import run_new
from website.apps.ts_om.models import Simulation


class RunNewTest(TestCase):
    def test_failure(self):
        simulation = Simulation.objects.create()
        simulation.set_input_file("")
        run_new.main(simulation.id)
        simulation.refresh_from_db()
        self.assertEqual(simulation.status, Simulation.FAILED)
        self.assertEqual("Exit code: 66", simulation.last_error_message)
        model_stdout = simulation.model_stdout.read()
        self.assertIn("XSD error", model_stdout)
        self.assertIn("invalid document structure", model_stdout)

    def test_success(self):
        simulation = Simulation.objects.create()
        with open(os.path.join(settings.BASE_DIR, "website", "apps", "ts_om", "tests", "data", "default.xml")) as fp:
            simulation.set_input_file(fp)
        run_new.main(simulation.id)
        simulation.refresh_from_db()
        self.assertEqual(simulation.status, Simulation.COMPLETE)
        self.assertEqual("", simulation.last_error_message)
        model_stdout = simulation.model_stdout.read()
        self.assertIn("100%", model_stdout)
        output = simulation.output_file.read()
        self.assertNotEqual(output, "")
        ctsout = simulation.ctsout_file.read()
        self.assertNotEqual(ctsout, "")
