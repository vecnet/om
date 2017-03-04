# Copyright (C) 2016, University of Notre Dame
# All rights reserved
import os
from django.test.testcases import TestCase

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
        with open(os.path.join("website", "apps", "ts_om", "tests", "data", "default.xml")) as fp:
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
