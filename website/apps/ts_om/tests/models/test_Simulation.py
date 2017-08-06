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
from django.core.files.base import File
from django.test.testcases import TestCase

from website.apps.ts_om.models import Simulation
from website.apps.ts_om.tests.factories import get_xml_as_fp


class SimulationModelTest(TestCase):
    def setUp(self):
        self.simulation = Simulation.objects.create()
    def test_unicode(self):
        self.assertEqual(str(self.simulation), str(self.simulation.id))

    def test_set_ctsout_file_as_string(self):
        self.simulation.set_ctsout_file("Test file")
        self.assertEqual(self.simulation.ctsout_file.read(), "Test file")

    def test_set_ctsout_file_as_file_object(self):
        fp = get_xml_as_fp("file.txt")
        self.simulation.set_ctsout_file(fp)
        fp.close()
        self.assertEqual(self.simulation.ctsout_file.read(), "Content of the file")

    def test_set_ctsout_file_as_django_file_object(self):
        fp = get_xml_as_fp("file.txt")
        file_object = File(fp)
        self.simulation.set_ctsout_file(file_object)
        fp.close()
        self.assertEqual(self.simulation.ctsout_file.read(), "Content of the file")

    def test_set_model_stdout_as_string(self):
        self.simulation.set_model_stdout("Test file")
        self.assertEqual(self.simulation.model_stdout.read(), "Test file")

    def test_set_model_stdout_as_file_object(self):
        fp = get_xml_as_fp("file.txt")
        self.simulation.set_model_stdout(fp)
        fp.close()
        self.assertEqual(self.simulation.model_stdout.read(), "Content of the file")

    def test_set_model_stdout_as_django_file_object(self):
        fp = get_xml_as_fp("file.txt")
        file_object = File(fp)
        self.simulation.set_model_stdout(file_object)
        fp.close()
        self.assertEqual(self.simulation.model_stdout.read(), "Content of the file")
