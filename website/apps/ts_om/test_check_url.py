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

from django.test import TestCase

from website.apps.ts_om.check import check_url


class CheckUrlTest(TestCase):
    def setUp(self):
        pass

    def test_1(self):
        self.assertEqual(check_url("http://google.com", ""), "http://google.com/")

    def test_2(self):
        self.assertEqual(check_url("http://google.com/", "validate"), "http://google.com/")

    def test_3(self):
        self.assertEqual(check_url("", "validate"), "http://127.0.0.1:8000/om_validate/validate/")

    def test_4(self):
        self.assertEqual(check_url(None, "validate"), "http://127.0.0.1:8000/om_validate/validate/")
