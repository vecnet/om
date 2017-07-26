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

import os

from django.urls import reverse
from django.test.client import Client
from django.test.testcases import TestCase
from mock.mock import patch

from website.apps.ts_om.tests.factories import ScenarioFactory, UserFactory, SimulationFactory
from website.notification import DANGER, SUCCESS


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files")


def get_xml(filename="group 8 baseline p2.xml"):
    with open(os.path.join(DATA_DIR, filename)) as fp:
        xml = fp.read()
    return xml


class ScenarioSummaryViewTest(TestCase):
    def setUp(self):
        self.scenario = ScenarioFactory()
        self.url = reverse("ts_om.summary", kwargs={"scenario_id": self.scenario.id})
        self.client.login(username=self.scenario.user.username, password="1")
        self.data = {
            "name": "Scenario",
            "desc": "Scenario Description",
            "xml": "mmm"
        }

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

    def test_get_broken_xml(self):
        self.scenario.xml = "<"
        self.scenario.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

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

    def test_post_broken_xml(self):
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.url)
        self.assertEqual(self.client.session["notifications"][0]["type"], DANGER)

    def test_post_success(self):
        self.data['xml'] = get_xml()
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('ts_om.list'))
        self.assertEqual(self.client.session["notifications"][0]["type"], SUCCESS)

    @patch("website.apps.ts_om_edit.views.ScenarioSummaryView.submit.submit")
    def test_post_save_and_run_failed(self, submit_func):
        submit_func.return_value = None
        self.data['xml'] = get_xml()
        self.data['submit_run'] = "Save and Run"
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('ts_om.list'))
        self.assertEqual(len(self.client.session["notifications"]), 2)
        # print(self.client.session["notifications"][0]["message"])
        # print(self.client.session["notifications"][1]["message"])
        self.assertEqual(self.client.session["notifications"][0]["type"], DANGER)  # Can't submit the simulation
        self.assertEqual(self.client.session["notifications"][1]["type"], SUCCESS) # Scenario saved successfully
        self.assertEqual(submit_func.called, True)

    @patch("website.apps.ts_om_edit.views.ScenarioSummaryView.submit.submit")
    def test_post_save_and_run_success(self, submit_func):
        simulation = SimulationFactory()
        submit_func.return_value = simulation
        self.data['xml'] = get_xml()
        self.data['submit_run'] = "Save and Run"
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('ts_om.list'))
        self.assertEqual(len(self.client.session["notifications"]), 2)
        # print(self.client.session["notifications"][0]["message"])
        # print(self.client.session["notifications"][1]["message"])
        self.assertEqual(self.client.session["notifications"][0]["type"], SUCCESS)  # Submitted successfully
        self.assertEqual(self.client.session["notifications"][1]["type"], SUCCESS) # Scenario saved successfully
        self.assertEqual(submit_func.called, True)
