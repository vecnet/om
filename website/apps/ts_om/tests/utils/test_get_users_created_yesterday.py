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
import datetime
from django.test.testcases import TestCase
from django.views.generic.dates import timezone_today

from website.apps.ts_om.tests.factories import UserFactory
from website.apps.ts_om.utils import get_users_created_yesterday


class GetUsersCreatedYesterdayTest(TestCase):
    def test_1(self):
        self.assertEqual(list(get_users_created_yesterday()), [])

    def test_2(self):
        user = UserFactory(date_joined=timezone_today() - datetime.timedelta(1))
        self.assertEqual(list(get_users_created_yesterday()), [user])

