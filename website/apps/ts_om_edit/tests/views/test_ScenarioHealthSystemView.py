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

from django.test import override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.test.client import Client
from django.test.testcases import TestCase
from vecnet.openmalaria.healthsystem import get_prob_from_percentage
from vecnet.openmalaria.scenario import Scenario

from website.apps.ts_om.models import Scenario as ScenarioModel

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ScenarioViewsTest(TestCase):
    fixtures = ["DemographicsSnippets", "AnophelesSnippets", "Interventions"]

    @override_settings(CSRF_COOKIE_SECURE=False)
    def setUp(self):
        self.client = Client()
        user = User.objects.create(username="user")
        user.set_password("user")
        user.save()
        self.user = user
        self.client.login(username="user", password="user")
        xml_filename = os.path.join(BASE_DIR, "files", "group 8 baseline p2.xml")
        self.model_scenario = None
        with open(xml_filename) as xml_file:
            self.model_scenario = ScenarioModel.objects.create(xml=xml_file.read(), user=self.user)
        self.url = reverse("ts_om.healthsystem", kwargs={"scenario_id": self.model_scenario.id})

    def test_get_healthsystem_view(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_post_healthsystem_view(self):
        scenario = Scenario(self.model_scenario.xml)

        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.name, "Kenya ACT")
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.firstLine, "ACT")
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.secondLine, "QN")
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.pSeekOfficialCareSevere, 0.48)
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.pSeekOfficialCareUncomplicated1, 0.04)
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.pSeekOfficialCareUncomplicated2, 0.04)
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.pSelfTreatUncomplicated, 0.0212)

        perc_total = 20
        perc_formal = 40
        expected_prob_total = get_prob_from_percentage(perc_total)
        expected_prob_formal = get_prob_from_percentage(100-perc_formal)
        post_data = {
            "perc_total_treated": str(perc_total),
            "perc_formal_care": str(perc_formal),
            "first_line_drug": "SP",
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(response.status_code, 302)

        model_scenario = ScenarioModel.objects.get(id=self.model_scenario.id)
        scenario = Scenario(model_scenario.xml)

        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.name, "Kenya ACT")
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.firstLine, "SP")
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.secondLine, "QN")
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.pSeekOfficialCareSevere, 0.48)
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.pSeekOfficialCareUncomplicated1, expected_prob_total)
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.pSeekOfficialCareUncomplicated2, expected_prob_total)
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.pSelfTreatUncomplicated, expected_prob_formal)
