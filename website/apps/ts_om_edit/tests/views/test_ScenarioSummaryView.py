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

from django.urls import reverse
from django.test.client import Client
from django.test.testcases import TestCase

from website.apps.ts_om.tests.factories import ScenarioFactory, UserFactory


class ScenarioSummaryViewTest(TestCase):
    def setUp(self):
        self.scenario = ScenarioFactory()
        self.url = reverse("ts_om.summary", kwargs={"scenario_id": self.scenario.id})
        self.client.login(username=self.scenario.user.username, password="1")

    def test_get_as_anonymous(self):
        client = Client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login") + "?next=" + self.url, response.url)

    def test_get_as_different_user(self):
        client = Client()
        user = UserFactory()
        client.login(username=user.username, password="1")
        response = client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["scenario"], self.scenario)
        self.assertEqual(
            ['arabiensis', 'funestus', 'minor', 'gambiae'],
            [vector.mosquito for vector in response.context["vectors"]]
        )

    def test_post_as_anonymous(self):
        client = Client()
        response = client.post(self.url, data={})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login") + "?next=" + self.url, response.url)

    def test_post_as_different_user(self):
        client = Client()
        user = UserFactory()
        client.login(username=user.username, password="1")
        response = client.post(self.url, data={})
        self.assertEqual(response.status_code, 403)

    def test_get_broken_xml(self):
        self.scenario.xml = "<"
        self.scenario.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
