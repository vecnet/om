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

from website.apps.big_brother.models import TrackingCode


class TrackingCodeModelTest(TestCase):
    def test_str(self):
        tracking_code = TrackingCode.objects.create(code="CODE")
        self.assertEqual(str(tracking_code), "CODE")