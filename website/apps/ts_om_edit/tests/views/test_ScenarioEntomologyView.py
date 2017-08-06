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
import json

from django.test import override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.test.client import Client
from django.test.testcases import TestCase
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
        self.url = reverse("ts_om.entomology", kwargs={"scenario_id": self.model_scenario.id})

    def test_get_entomology_view(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_post_entomology_view(self):
        scenario = Scenario(self.model_scenario.xml)

        self.assertEqual(scenario.entomology.name, "one species")
        self.assertEqual(scenario.entomology.scaledAnnualEIR, 16)
        self.assertEqual(len(scenario.entomology.vectors), 1)

        vector = scenario.entomology.vectors["gambiae"]
        self.assertEqual(vector.mosquito, "gambiae")
        self.assertEqual(vector.propInfected, 0.078)
        self.assertEqual(vector.propInfectious, 0.015)
        self.assertEqual(vector.seasonality.annualEIR, 1)

        annual_eir = 25
        perc_average_eir = 6
        expected_average_eir = perc_average_eir / 100.0
        perc_human_blood_index = 50
        expected_human_blood_index = perc_human_blood_index / 100.0
        monthly_values = [0.121950947577, 0.150033433731, 0.135783169538, 0.142507307385, 0.12160516792, 0.132069391,
                          0.14132650592, 0.12974214888, 0.10223384536, 0.08159456812, 0.0673589848, 0.08462085352]
        post_data = {
            "form-TOTAL_FORMS": 1,
            "form-INITIAL_FORMS": 1,
            "form-MIN_FORMS": 0,
            "form-MAX_FORMS": 1000,
            "annual_eir": annual_eir,
            "form-0-average_eir": perc_average_eir,
            "form-0-human_blood_index": perc_human_blood_index,
            "form-0-monthly_values": json.dumps(monthly_values),
            "form-0-name": "arabiensis",
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(response.status_code, 302)

        model_scenario = ScenarioModel.objects.get(id=self.model_scenario.id)
        scenario = Scenario(model_scenario.xml)

        self.assertEqual(scenario.entomology.scaledAnnualEIR, annual_eir)
        self.assertEqual(len(scenario.entomology.vectors), 1)

        self.assertRaises(KeyError, lambda: scenario.entomology.vectors["gambiae"])
        vector = scenario.entomology.vectors["arabiensis"]

        self.assertEqual(vector.mosquito, "arabiensis")
        self.assertEqual(vector.propInfected, 0.078)
        self.assertEqual(vector.propInfectious, 0.015)
        self.assertEqual(vector.seasonality.annualEIR, expected_average_eir)
        self.assertEqual(vector.mosq.mosqHumanBloodIndex, expected_human_blood_index)
        self.assertEqual(vector.seasonality.monthlyValues, monthly_values)