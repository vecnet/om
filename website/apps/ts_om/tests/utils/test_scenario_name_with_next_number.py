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

from website.apps.ts_om.utils import scenario_name_with_next_number


class GetNumberAtTheEndOfStringTest(TestCase):
    def test_1(self):
        self.assertEqual(scenario_name_with_next_number(""), " - 2")

    def test_2(self):
        self.assertEqual(scenario_name_with_next_number(" - 2"), "- 3")

    def test_3(self):
        self.assertEqual(scenario_name_with_next_number("Scenario"), "Scenario - 2")

    def test_4(self):
        self.assertEqual(scenario_name_with_next_number("Scenario"), "Scenario - 2")

    def test_5(self):
        self.assertEqual(scenario_name_with_next_number("Scenario 1"), "Scenario 2")

    def test_6(self):
        self.assertEqual(scenario_name_with_next_number("Scenario - 2"), "Scenario - 3")

    def test_7(self):
        self.assertEqual(scenario_name_with_next_number("Scenario - 9"), "Scenario - 10")

    def test_8(self):
        self.assertEqual(scenario_name_with_next_number("Scenario - 999"), "Scenario - 1000")

    def test_9(self):
        self.assertEqual(scenario_name_with_next_number("Scenario999"), "Scenario1000")

    def test_10(self):
        self.assertEqual(scenario_name_with_next_number("Scenario #123"), "Scenario #124")
