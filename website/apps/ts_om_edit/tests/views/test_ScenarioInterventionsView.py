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

import json
import os
import urllib.request, urllib.parse, urllib.error

from django.contrib.auth.models import User
from django.http import QueryDict
from django.test import TestCase
from django.test.client import Client

from django.urls import reverse

from website.apps.ts_om_edit.views.ScenarioInterventionsView import parse_parameters, parse_options, inner_parse_options
from vecnet.openmalaria.scenario import Scenario

from website.apps.ts_om.models import Scenario as ScenarioModel


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ScenarioInterventionsViewUtilsTest(TestCase):
    post_data = None
    query_dict = None

    def setUp(self):
        json_filename = os.path.join(BASE_DIR, "files", "test_data.json")
        with open(json_filename) as json_file:
            json_data = json.load(json_file)
            self.post_data = json_data["interventions-post-data"]
            query_string = urllib.parse.urlencode(self.post_data)
            self.query_dict = QueryDict(query_string=query_string)

    def test_post_data(self):
        self.assertIsNotNone(self.post_data)
        self.assertIn("gvi-TOTAL_FORMS", self.post_data)

    def test_parse_parameters(self):
        parsed_data = parse_parameters(self.query_dict, prefix="gvi")

        self.assertEqual(len(parsed_data), 1)

        data_point = parsed_data[0]
        self.assertIn("deterrency", data_point)
        self.assertEqual(data_point["deterrency"], "0.25")
        self.assertIn("mosquito", data_point)
        self.assertEqual(data_point["mosquito"], "gambiae")

    def test_parse_options(self):
        parsed_data = parse_options(self.query_dict, prefix="mda")

        self.assertEqual(len(parsed_data), 1)
        data_point = parsed_data[0]
        self.assertIn("pSelection", data_point)
        self.assertEqual(data_point["pSelection"], "0.0")
        self.assertIn("deploys", data_point)
        self.assertEqual(len(data_point["deploys"]), 1)
        deploy = data_point["deploys"][0]
        self.assertIn("components", deploy)
        self.assertEqual(deploy["components"], "test")

    def test_inner_parse_options_none_1(self):
        self.assertFalse(inner_parse_options(None, {}, "test"))

    def test_inner_parse_options_none_2(self):
        self.assertFalse(inner_parse_options("Test", None, "test"))


class ScenarioViewsTest(TestCase):
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

    def test_get_interventions_view(self):
        response = self.client.get(reverse("ts_om.interventions", kwargs={"scenario_id": self.model_scenario.id}))

        self.assertEqual(response.status_code, 200)

    def test_post_interventions_view(self):
        scenario = Scenario(self.model_scenario.xml)

        self.assertEqual(len(scenario.interventions.human), 3)
        intervention = scenario.interventions.human["ActellicBased"]
        self.assertEqual(intervention.id, "ActellicBased")
        self.assertEqual(intervention.name, "IRS")
        self.assertEqual(len(intervention.anophelesParams), 1)
        anopheles_params = intervention.anophelesParams[0]
        self.assertEqual(anopheles_params.mosquito, "gambiae")
        self.assertEqual(anopheles_params.propActive, 0.45)
        self.assertEqual(anopheles_params.deterrency, -0.23)
        self.assertEqual(anopheles_params.preprandialKillingEffect , 0.1)
        self.assertEqual(anopheles_params.postprandialKillingEffect , 0.5)
        self.assertEqual(len(scenario.interventions.human.deployments), 3)

        scenario.interventions.human.deployments = []
        self.assertEqual(len(scenario.interventions.human.deployments), 0)

        post_data = {
            "gvi-TOTAL_FORMS": 1,
            "gvi-INITIAL_FORMS": 0,
            "gvi-MIN_FORMS": 0,
            "gvi-MAX_FORMS": 1000,
            "llin-TOTAL_FORMS": 0,
            "llin-INITIAL_FORMS": 0,
            "llin-MIN_FORMS": 0,
            "llin-MAX_FORMS": 1000,
            "irs-TOTAL_FORMS": 0,
            "irs-INITIAL_FORMS": 0,
            "irs-MIN_FORMS": 0,
            "irs-MAX_FORMS": 1000,
            "pyrethroids-TOTAL_FORMS": 0,
            "pyrethroids-INITIAL_FORMS": 0,
            "pyrethroids-MIN_FORMS": 0,
            "pyrethroids-MAX_FORMS": 1000,
            "ddt-TOTAL_FORMS": 0,
            "ddt-INITIAL_FORMS": 0,
            "ddt-MIN_FORMS": 0,
            "ddt-MAX_FORMS": 1000,
            "larviciding-TOTAL_FORMS": 0,
            "larviciding-INITIAL_FORMS": 0,
            "larviciding-MIN_FORMS": 0,
            "larviciding-MAX_FORMS": 1000,
            "mda-TOTAL_FORMS": 0,
            "mda-INITIAL_FORMS": 0,
            "mda-MIN_FORMS": 0,
            "mda-MAX_FORMS": 1000,
            "vaccine-bsv-TOTAL_FORMS": 0,
            "vaccine-bsv-INITIAL_FORMS": 0,
            "vaccine-bsv-MIN_FORMS": 0,
            "vaccine-bsv-MAX_FORMS": 1000,
            "vaccine-pev-TOTAL_FORMS": 0,
            "vaccine-pev-INITIAL_FORMS": 0,
            "vaccine-pev-MIN_FORMS": 0,
            "vaccine-pev-MAX_FORMS": 1000,
            "vaccine-tbv-TOTAL_FORMS": 0,
            "vaccine-tbv-INITIAL_FORMS": 0,
            "vaccine-tbv-MIN_FORMS": 0,
            "vaccine-tbv-MAX_FORMS": 1000,
            "gvi-0-id": "test",
            "gvi-0-name": "GVI",
            "gvi-0-attrition": 50,
            "gvi-0-vector_0_mosquito": "gambiae",
            "gvi-0-vector_0_propActive": 0.1,
            "gvi-0-vector_0_deterrency": 0.25,
            "gvi-0-vector_0_preprandialKillingEffect ": 0.2,
            "gvi-0-vector_0_postprandialKillingEffect ": 0.44,
        }
        response = self.client.post(reverse("ts_om.interventions", kwargs={"scenario_id": self.model_scenario.id}),
                                    post_data)
        self.assertEqual(response.status_code, 302)

        model_scenario = ScenarioModel.objects.get(id=self.model_scenario.id)
        scenario = Scenario(model_scenario.xml)

        self.assertEqual(len(scenario.interventions.human), 1)
        self.assertRaises(KeyError, lambda: scenario.interventions.human["ActellicBased"])

        intervention = scenario.interventions.human["test"]
        self.assertEqual(intervention.id, "test")
        self.assertEqual(intervention.name, "GVI")
        self.assertEqual(len(intervention.anophelesParams), 1)

        anopheles_params = intervention.anophelesParams[0]
        self.assertEqual(anopheles_params.mosquito, "gambiae")
        self.assertEqual(anopheles_params.propActive, 0.1)
        self.assertEqual(anopheles_params.deterrency, 0.25)
        self.assertEqual(anopheles_params.preprandialKillingEffect , 0.2)
        self.assertEqual(anopheles_params.postprandialKillingEffect , 0.44)
