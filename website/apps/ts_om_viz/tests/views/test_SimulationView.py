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
from django.test import Client
from django.test.testcases import TestCase
from django.urls.base import reverse

from website.apps.ts_om.models import Simulation
from website.apps.ts_om.tests.factories import UserFactory, ScenarioFactory
from website.apps.ts_om_viz.tests.views.test_get_survey_data_view import create_scenario_from_directory
from website.notification import DANGER


class SimulationViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.scenario = create_scenario_from_directory(user=self.user, directory="gambiae")
        self.simulation = self.scenario.new_simulation
        self.url = reverse("ts_om_viz.SimulationView", kwargs={"id": self.simulation.id})
        self.client.login(username=self.user.username, password="1")

    def test_no_permission(self):
        another_user = UserFactory()
        client = Client()
        client.login(username=another_user.username, password="1")
        response = client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertNotIn("simulation", response.context)

    def test_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("simulation", response.context)

    # def test_success_with_querystring_mosquito(self):
    #     response = self.client.get(self.url + "?survey_measure_id=1&survey_third_dimension=gambiae")
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.context["survey_measure_id"], "1")
    #     self.assertEqual(response.context["survey_third_dimension"], "gambiae")

    def test_success_with_querystring(self):
        response = self.client.get(self.url + "?survey_measure_id=1&survey_third_dimension=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["survey_measure_id"], 1)
        self.assertEqual(response.context["survey_third_dimension"], 2)

    def test_empty_simulation(self):
        simulation = Simulation.objects.create()
        scenario = ScenarioFactory(user=self.user, xml="", new_simulation=simulation)
        url = reverse("ts_om_viz.SimulationView", kwargs={"id": simulation.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Error processing input or output files", response.content)
        self.assertEqual(response.context["simulation"], simulation)
        self.assertEqual(response.context["output_txt_filename"], None)
        self.assertEqual(response.context["ctsout_txt_filename"], None)
        self.assertNotIn("xml_filename", response.context)
        self.assertNotIn("model_stdout", response.context)

    def test_no_output_txt(self):
        self.simulation.output_file = None
        self.simulation.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("simulation", response.context)
        self.assertEqual(response.context["survey_measures"], {})
        self.assertNotEqual(response.context["cts_measures"], {})

    def test_no_ctsout_txt(self):
        self.simulation.ctsout_file = None
        self.simulation.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("simulation", response.context)
        self.assertEqual(response.context["cts_measures"], {})
        self.assertNotEqual(response.context["survey_measures"], {})
