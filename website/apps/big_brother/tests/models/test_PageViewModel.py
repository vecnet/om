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
from django.test import TestCase

from website.apps.big_brother.models import PageVisit


class PageViewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user")

    def test_str(self):
        page_visit = PageVisit.objects.create(user_id=self.user.id, url="/subject_manager/")
        self.assertEqual(page_visit.url, "/subject_manager/")
        self.assertEqual(str(page_visit), "/subject_manager/")