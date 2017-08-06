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

from django.contrib.auth.models import User
from django.urls import reverse
from django.test.client import Client
from vecnet.openmalaria.scenario import Scenario

from website.apps.ts_om.models import Scenario as ScenarioModel, DemographicsSnippet

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from django.test import TestCase


class ScenarioDemographyViewTest(TestCase):
    fixtures = ["DemographicsSnippets", "AnophelesSnippets", "Interventions"]

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

    def test_get_demography_view(self):
        response = self.client.get(reverse("ts_om.demography", kwargs={"scenario_id": self.model_scenario.id}))

        self.assertEqual(response.status_code, 200)

    def test_post_demography_view(self):
        scenario = Scenario(self.model_scenario.xml)
        self.assertEqual(scenario.demography.name, "Ifakara")
        self.assertEqual(scenario.demography.maximumAgeYrs, 90)
        self.assertEqual(scenario.demography.popSize, 1000)

        demographics_snippet = DemographicsSnippet.objects.get(name="Rachuonyo")
        self.assertIsNotNone(demographics_snippet)

        new_age_dist_xml = demographics_snippet.xml

        post_data = {
            "age_dist": "Rachuonyo",
            "age_dist_name": "Rachuonyo",
            "age_dist_xml": new_age_dist_xml,
            "maximum_age_yrs": "90",
            "human_pop_size": "100"
        }
        response = self.client.post(reverse("ts_om.demography", kwargs={"scenario_id": self.model_scenario.id}),
                                    post_data)
        self.assertEqual(response.status_code, 302)

        model_scenario = ScenarioModel.objects.get(id=self.model_scenario.id)
        scenario = Scenario(model_scenario.xml)

        self.assertEqual(scenario.demography.name, "Rachuonyo")
        self.assertEqual(scenario.demography.maximumAgeYrs, 90)
        self.assertEqual(scenario.demography.popSize, 100)
        self.assertEqual(scenario.demography.ageGroup.lowerbound, 0)
        self.assertEqual(float(scenario.demography.ageGroup.group[1]["upperbound"]), 5.0)
        self.assertEqual(float(scenario.demography.ageGroup.group[1]["poppercent"]), 13.1)
