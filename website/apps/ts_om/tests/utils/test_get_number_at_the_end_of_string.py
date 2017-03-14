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

from website.apps.ts_om.utils import get_number_at_the_end_of_string


class GetNumberAtTheEndOfStringTest(TestCase):
    def test_1(self):
        self.assertEqual(get_number_at_the_end_of_string(""), None)

    def test_2(self):
        self.assertEqual(get_number_at_the_end_of_string("Test"), None)

    def test_3(self):
        self.assertEqual(get_number_at_the_end_of_string(" "), None)

    def test_4(self):
        self.assertEqual(get_number_at_the_end_of_string("1"), 1)

    def test_5(self):
        self.assertEqual(get_number_at_the_end_of_string("0"), 0)

    def test_6(self):
        self.assertEqual(get_number_at_the_end_of_string("999"), 999)

    def test_7(self):
        self.assertEqual(get_number_at_the_end_of_string("1234567890"), 1234567890)

    def test_8(self):
        self.assertEqual(get_number_at_the_end_of_string("0123456789"), 123456789)

    def test_9(self):
        self.assertEqual(get_number_at_the_end_of_string("Scenario - 1"), 1)

    def test_10(self):
        self.assertEqual(get_number_at_the_end_of_string("Scenario - 123"), 123)

    def test_11(self):
        self.assertEqual(get_number_at_the_end_of_string("Sce456nario - 123"), 123)

    def test_12(self):
        self.assertEqual(get_number_at_the_end_of_string("Scenario - 123.456"), 456)

    def test_13(self):
        self.assertEqual(get_number_at_the_end_of_string("Scenario - 0"), 0)
