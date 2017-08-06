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
        self.url = reverse("ts_om.monitoring", kwargs={"scenario_id": self.model_scenario.id})

    def test_get_scenario_monitoring_view(self):
        self.assertIsNotNone(self.model_scenario)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_scenario_monitoring_view(self):
        scenario = Scenario(self.model_scenario.xml)
        self.assertListEqual(scenario.monitoring.SurveyOptions, ["nUncomp"])

        post_data = {
            "sim_start_date": 2015,
            "monitor_yrs": 10,
            "monitor_mos": 0,
            "monitor_start_date": 2025,
            "measure_outputs": "yearly",
            "parasite_detection_diagnostic_type": 100,
            "nr_per_age_group": "true",
            "patent_infections": "true"
        }
        response = self.client.post(self.url, post_data)

        self.assertEqual(response.status_code, 302)

        model_scenario = ScenarioModel.objects.get(id=self.model_scenario.id)
        scenario = Scenario(model_scenario.xml)

        self.assertListEqual(scenario.monitoring.SurveyOptions, ["nHost", "nPatent"])
