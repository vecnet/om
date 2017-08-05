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
from django.test.client import Client
from django.test.testcases import TestCase
from django.urls.base import reverse

from website.apps.ts_om.tests.factories import ScenarioFactory, UserFactory
from website.notification import DANGER, SUCCESS


class DeleteScenarioViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.scenario = ScenarioFactory(user=self.user)
        self.client.login(username=self.user.username, password="1")
        self.url = reverse("ts_om.delete", kwargs={"scenario_id": self.scenario.id})

    def test_as_anonymous(self):
        client = Client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.scenario.refresh_from_db()
        self.assertEqual(self.scenario.deleted, False)

    def test_no_permission(self):
        user = UserFactory()
        client = Client()
        client.login(username=user.username, password="1")
        response = client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.scenario.refresh_from_db()
        self.assertEqual(self.scenario.deleted, False)

    def test_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session["notifications"][0]["type"], SUCCESS)
        self.assertEqual(response.url, reverse("ts_om.list"))
        self.scenario.refresh_from_db()
        self.assertEqual(self.scenario.deleted, True)

    def test_success_undelete(self):
        self.scenario.deleted = True
        self.scenario.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session["notifications"][0]["type"], SUCCESS)
        self.assertEqual(response.url, reverse("ts_om.list"))
        self.scenario.refresh_from_db()
        self.assertEqual(self.scenario.deleted, False)
