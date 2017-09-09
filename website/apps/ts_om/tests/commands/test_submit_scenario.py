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
from django.core.management import call_command
from django.test.testcases import TestCase

from website.apps.ts_om.tests.factories import ScenarioFactory


class SubmitScenarioTest(TestCase):
    def setUp(self):
        self.scenario = ScenarioFactory()

    def test_scenario_doesnt_exist(self):
        call_command("submit_scenario", 1000000, wait=True)
        # Make sure that there is no exception
        self.assertTrue(True)

    def test_success(self):
        call_command("submit_scenario", self.scenario.id)
        # Make sure that there is no exception
        self.assertTrue(True)
