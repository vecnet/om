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

from django.contrib.auth.models import User
from django.test.testcases import TestCase
from django.urls.base import reverse


class MacedFilterTest(TestCase):
    def test(self):
        user = User.objects.create(username='admin', is_superuser=True, is_staff=True)
        user.set_password('1')
        user.save()
        self.client.login(username='admin', password='1')
        url = reverse('admin:big_brother_pagevisit_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_filter_active(self):
        user = User.objects.create(username='admin', is_superuser=True, is_staff=True)
        user.set_password('1')
        user.save()
        self.client.login(username='admin', password='1')
        url = reverse('admin:big_brother_pagevisit_changelist') + "?shoe_maced_items=Yes"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
