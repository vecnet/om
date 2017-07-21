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

from django.urls import reverse
from django.test.client import Client
from django.test.testcases import TestCase
from mock.mock import patch

from website.apps.ts_om.tests.factories import ScenarioFactory

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


class SubmitScenariosViewTest(TestCase):
    def setUp(self):
        self.scenario = ScenarioFactory()
        self.user = self.scenario.user
        self.user.set_password("1")
        self.user.save()

    @patch("website.apps.ts_om.views.submit_scenarios_view.submit")
    def test_anonymous(self, submit_func):
        client = Client()
        data = {"scenario_ids": json.dumps([self.scenario.id])}
        response = client.post(reverse("ts_om.submit"), data=data)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        self.assertEqual(response_json["ok"], False)
        self.scenario.refresh_from_db()
        self.assertEqual(submit_func.called, False)

    @patch("website.apps.ts_om.views.submit_scenarios_view.submit")
    @patch("website.apps.ts_om.views.submit_scenarios_view.rest_validate")
    def test_success(self, rest_validate_func, submit_func):
        rest_validate_func.return_value = json.dumps({'result':0})
        client = Client()
        client.login(username=self.user.username, password="1")
        data = {"scenario_ids": json.dumps([self.scenario.id])}
        response = client.post(reverse("ts_om.submit"), data=data)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        self.assertEqual(response_json["ok"], True)
        self.scenario.refresh_from_db()
        self.assertEqual(rest_validate_func.called, True)
        self.assertEqual(submit_func.called, True)

    @patch("website.apps.ts_om.views.submit_scenarios_view.submit")
    @patch("website.apps.ts_om.views.submit_scenarios_view.rest_validate")
    def test_validation_fails(self, rest_validate_func, submit_func):
        rest_validate_func.return_value = json.dumps({'result':66})
        client = Client()
        client.login(username=self.user.username, password="1")
        data = {"scenario_ids": json.dumps([self.scenario.id])}
        response = client.post(reverse("ts_om.submit"), data=data)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        # self.assertEqual(response_json["ok"], False)
        self.scenario.refresh_from_db()
        self.assertEqual(rest_validate_func.called, True)
        self.assertEqual(submit_func.called, False)
