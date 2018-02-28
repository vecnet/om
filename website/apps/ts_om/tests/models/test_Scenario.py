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

from website.apps.ts_om.models import Simulation
from website.apps.ts_om.tests.factories import ScenarioFactory, get_xml


class ScenarioTest(TestCase):
    def test_demography_property_1(self):
        scenario = ScenarioFactory(xml=get_xml("tororo.xml"))
        self.assertEqual(scenario.demography.name, "Tororo")

    def test_demography_property_2(self):
        scenario = ScenarioFactory(xml="xml")
        self.assertEqual(scenario.demography, "no_name")

    def test_output_file_property_1(self):
        scenario = ScenarioFactory(xml=get_xml("tororo.xml"))
        self.assertEqual(scenario.output_file, None)

    def test_output_file_property_2(self):
        scenario = ScenarioFactory(xml=get_xml("tororo.xml"))
        scenario.new_simulation = Simulation.objects.create()
        scenario.save()
        self.assertEqual(scenario.output_file, None)

    def test_output_file_property_3(self):
        scenario = ScenarioFactory(xml=get_xml("tororo.xml"))
        scenario.new_simulation = Simulation.objects.create()
        scenario.save()
        scenario.new_simulation.set_model_stdout("123")
        self.assertEqual(scenario.output_file.read(), b"123")

