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

import json
import os

from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test.testcases import TestCase
from mock.mock import patch

from website.apps.ts_om.tests.factories import ScenarioFactory, UserFactory

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


class SubmitScenariosViewTest(TestCase):
    def setUp(self):
        self.scenario = ScenarioFactory()
        self.user = self.scenario.user
        self.user.set_password("1")
        self.user.save()
        self.url = reverse("ts_om.download", kwargs={"scenario_id": self.scenario.id})

    def test_anonymous(self):
        client = Client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_success(self):
        client = Client()
        client.login(username=self.user.username, password="1")
        response = client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('<demography maximumAgeYrs="90" name="Rachuonyo" popSize="100">', response.content)

    def test_wrong_user(self):
        client = Client()
        user = UserFactory()
        client.login(username=user.username, password="1")
        response = client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_no_scenario(self):
        client = Client()
        client.login(username=self.user.username, password="1")
        url = reverse("ts_om.download", kwargs={"scenario_id": 1000000})
        response = client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_incorrect_xml(self):
        client = Client()
        self.scenario.xml = "123"
        self.scenario.save()
        client.login(username=self.user.username, password="1")
        response = client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "123")
