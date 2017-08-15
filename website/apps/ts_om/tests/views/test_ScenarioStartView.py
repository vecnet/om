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

import StringIO
from django.urls import reverse
from django.test.testcases import TestCase
from django.test.utils import override_settings

from website.apps.ts_om.models import Scenario, BaselineScenario
from website.apps.ts_om.tests.factories import UserFactory, get_xml


class ScenarioStartViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.login(username=self.user.username, password="1")
        self.url = reverse("ts_om.start")

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["scenario_id"], 0)

    def test_post_build_new(self):
        response = self.client.post(
            self.url,
            data={'name':'Brave New', 'desc':'Brave New Scenario', 'choice': 'build'}
        )
        self.assertEqual(response.status_code, 302)
        scenario = Scenario.objects.get(description="Brave New Scenario")
        self.assertIn(reverse('ts_om.monitoring', kwargs={'scenario_id': scenario.id}), response.url)
        self.assertEqual(scenario.name, "Brave New")
        self.assertIsNone(scenario.new_simulation)
        self.assertEqual(scenario.user, self.user)
        self.assertEqual(scenario.baseline, BaselineScenario.objects.get(name='Default'))

    def test_post_copy_baseline(self):
        baseline = BaselineScenario.objects.get(name="Western Kenya")
        response = self.client.post(
            self.url,
            data={'name':'Brave New', 'desc':'Brave New Scenario', 'choice': 'list', 'list': baseline.id}
        )
        self.assertEqual(response.status_code, 302)
        scenario = Scenario.objects.get(description="Brave New Scenario")
        self.assertIn(reverse('ts_om.monitoring', kwargs={'scenario_id': scenario.id}), response.url)
        self.assertEqual(scenario.name, "Brave New")
        self.assertIsNone(scenario.new_simulation)
        self.assertEqual(scenario.user, self.user)
        self.assertEqual(scenario.baseline, BaselineScenario.objects.get(name='Western Kenya'))


    def test_post_fail_baseline_no_baseline_id(self):
        response = self.client.post(
            self.url,
            data={'name':'Brave New', 'desc':'Brave New Scenario', 'choice': 'list'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["upload_error"], 'Error: Please specify baseline')
        self.assertFalse(Scenario.objects.filter(description="Brave New Scenario").exists())

    @override_settings(TS_OM_VALIDATE_URL=None)
    def test_post_upload_xml(self):
        xml = get_xml()
        response = self.client.post(
            self.url,
            data={'name': 'Brave New', 'desc': 'Brave New S', 'choice': 'upload', 'xml_file': StringIO.StringIO(xml)}
        )
        self.assertEqual(response.status_code, 302)
        scenario = Scenario.objects.get(description="Brave New S")
        self.assertIn(reverse('ts_om.monitoring', kwargs={'scenario_id': scenario.id}), response.url)
        self.assertEqual(scenario.name, "Brave New")
        self.assertIsNone(scenario.new_simulation)
        self.assertEqual(scenario.user, self.user)
        self.assertEqual(scenario.baseline, None)

    @override_settings(TS_OM_VALIDATE_URL=None)
    def test_post_upload_no_xml(self):
        xml = get_xml()
        response = self.client.post(
            self.url,
            data={'name': 'Brave New', 'desc': 'Brave New S', 'choice': 'upload'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Scenario.objects.count(), 0)
        # scenario = Scenario.objects.get(description="Brave New S")
        # self.assertIn(reverse('ts_om.monitoring', kwargs={'scenario_id': scenario.id}), response.url)
        # self.assertEqual(scenario.name, "Brave New")
        # self.assertIsNone(scenario.new_simulation)
        # self.assertEqual(scenario.user, self.user)
        # self.assertEqual(scenario.baseline, None)

    @override_settings(TS_OM_VALIDATE_URL=None)
    def test_post_upload_incorrect_xml(self):
        xml = "aaa"
        response = self.client.post(
            self.url,
            data={'name': 'Brave New', 'desc': 'Brave New S', 'choice': 'upload', 'xml_file': StringIO.StringIO(xml)}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Scenario.objects.count(), 0)
        self.assertIn("Error: Invalid openmalaria simulation uploaded.", response.content)
