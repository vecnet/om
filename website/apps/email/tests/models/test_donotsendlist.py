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

from django.db.utils import IntegrityError
from django.test.testcases import TestCase

from website.apps.email.models import DoNotSendEmailList


class DoNotSendEmailListTest(TestCase):
    def test_str(self):
        item = DoNotSendEmailList.objects.create(email="123@example.com")
        self.assertEqual(str(item), "123@example.com")

    def test_email_field_required(self):
        self.assertRaises(IntegrityError, DoNotSendEmailList.objects.create)
