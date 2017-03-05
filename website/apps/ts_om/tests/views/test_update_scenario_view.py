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

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test.testcases import TestCase

from website.apps.ts_om.models import Scenario


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


class UpdateScenarioViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user")
        self.user.set_password("1")
        self.user.save()
        with open(os.path.join(DATA_DIR, "default.xml")) as fp:
            self.xml = fp.read()
        with open(os.path.join(DATA_DIR, "default2.xml")) as fp:
            self.xml2 = fp.read()
        self.scenario = Scenario.objects.create(user=self.user, xml=self.xml, description="desc")

    def test_anonymous(self):
        client = Client()
        response = client.post(reverse("ts_om.scenario.update"), data={"scenario_id": self.scenario.id})
        self.assertEqual(response.status_code, 302)
        self.scenario.refresh_from_db()

        self.assertEqual(self.scenario.description, "desc")
        self.assertEqual(self.scenario.name, "Default scenario")
        self.assertEqual(self.scenario.xml, self.xml)

    def test_success_empty_response(self):
        client = Client()
        client.login(username="user", password="1")
        response = client.post(reverse("ts_om.scenario.update"), data={"scenario_id": self.scenario.id})
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertEqual(json_response["status"], "ok")
        self.scenario.refresh_from_db()

        self.assertEqual(self.scenario.description, "desc")
        self.assertEqual(self.scenario.name, "Default scenario")
        self.assertEqual(self.scenario.xml, self.xml)

    def test_success_update_everything(self):
        client = Client()
        client.login(username="user", password="1")
        data = {
            "scenario_id": self.scenario.id,
            "name": "Hello",
            "description": "Description_hello",
            "xml": self.xml2,
        }
        self.assertNotIn('<option name="human infectiousness" value="true"/>', self.scenario.xml)
        response = client.post(reverse("ts_om.scenario.update"), data=data)
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertEqual(json_response["status"], "ok")
        self.scenario.refresh_from_db()
        self.assertEqual(self.scenario.name, "Hello")
        self.assertEqual(self.scenario.description, "Description_hello")
        self.assertIn('<option name="human infectiousness" value="true"/>', self.scenario.xml)

