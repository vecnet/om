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

from django.urls import reverse
from django.test.client import Client
from django.test.testcases import TestCase

from website.apps.ts_om.models import Simulation
from website.apps.ts_om.tests.factories import ScenarioFactory, UserFactory

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def get_xml(filename="default.xml"):
    with open(os.path.join(DATA_DIR, filename)) as fp:
        xml = fp.read()
    return xml


class GetCtsDataViewTest(TestCase):
    def setUp(self):
        self.simulation = Simulation.objects.create(status=Simulation.COMPLETE)
        self.simulation.set_input_file(get_xml("scenario.xml"))
        self.simulation.set_output_file(get_xml("output.txt"))
        self.simulation.set_ctsout_file(get_xml("ctsout.txt"))
        self.simulation.set_model_stdout(get_xml("model_stdout_stderr.txt"))

        self.scenario = ScenarioFactory(xml=get_xml("scenario.xml"), new_simulation=self.simulation)
        self.user = self.scenario.user
        self.client.login(username=self.user, password="1")
        self.url = reverse(
            "ts_om_viz.get_cts_data",
            kwargs={"sim_id": self.scenario.new_simulation.id, "measure_name": "simulated EIR"}
        )

    def test_simulation_no_input_file(self):
        simulation = Simulation.objects.create(status=Simulation.COMPLETE)
        self.scenario.new_simulation = simulation
        self.scenario.save()
        url = reverse(
            "ts_om_viz.get_cts_data",
            kwargs={"sim_id": self.scenario.new_simulation.id, "measure_name": "simulated EIR"}
        )
        self.assertRaises(TypeError, self.client.get, url)

    def test_unknown_measure(self):
        url = reverse(
            "ts_om_viz.get_cts_data",
            kwargs={"sim_id": self.scenario.new_simulation.id, "measure_name": "simulated EIR1"}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        json_content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(json_content["sim_id"], self.scenario.new_simulation.id)
        self.assertEqual(json_content["data"][0], 0.00223318)
        self.assertEqual(json_content["data"][-1], 0.00290952)
        self.assertEqual(json_content["measure_name"], "simulated EIR")
        self.assertIn("description", json_content)

    def test_success_no_output_file(self):
        self.simulation.output_file = None
        self.simulation.model_stdout = None
        self.simulation.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        json_content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(json_content["sim_id"], self.scenario.new_simulation.id)
        self.assertEqual(json_content["data"][0], 0.00223318)
        self.assertEqual(json_content["data"][-1], 0.00290952)
        self.assertEqual(json_content["measure_name"], "simulated EIR")
        self.assertIn("description", json_content)

    def test_anonymous_user(self):
        client = Client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_different_user(self):
        client = Client()
        user = UserFactory()
        client.login(username=user.username, password="1")
        response = client.get(self.url)
        self.assertEqual(response.status_code, 403)

