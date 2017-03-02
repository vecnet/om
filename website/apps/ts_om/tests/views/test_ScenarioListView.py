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
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase

from website.apps.ts_om.models import Scenario


class ScenarioListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user")
        self.user.set_password("1")
        self.user.save()
        self.client.login(username="user", password="1")

    def test_empty_list(self):
        self.assertEqual(Scenario.objects.filter(user=self.user).count(), 0)
        response = self.client.get(reverse("ts_om.list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "<p>No simulations found</p>",
            response.content,
        )

    def test_incorrect_xml_example(self):
        scenario = Scenario.objects.create(
            user=self.user,
            xml="",
            description="Incorrect XML Example",
        )
        self.assertEqual(Scenario.objects.filter(user=self.user).count(), 1)
        response = self.client.get(reverse("ts_om.list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Incorrect XML Example",
            response.content,
        )
        self.assertIn(
            "XML Error",
            response.content,
        )

    def test_description_truncation(self):
        # Perhaps should use correct xml in this test
        scenario = Scenario.objects.create(
            user=self.user,
            xml="",
            description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce auctor molestie ex vel cursus. "
                        "Donec tortor magna, porttitor at ipsum placerat,"
        )
        response = self.client.get(reverse("ts_om.list"))
        self.assertEqual(response.status_code, 200)
        print response.content
        self.assertIn(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce auctor molestie ex vel cursus. Don...",
            response.content,
        )
