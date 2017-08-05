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

from django.contrib.auth.models import User
from django.urls import reverse
from django.test.client import Client
from django.test.testcases import TestCase

from website.apps.ts_om.models import Scenario, Simulation


def create_simulation(user, input_file=None, output_txt_file=None, ctsout_txt_file=None, model_output_file=None):
    simulation = Simulation.objects.create()
    if input_file:
        simulation.set_input_file(input_file)
    if output_txt_file:
        simulation.set_output_file(output_txt_file)
    if ctsout_txt_file:
        simulation.set_ctsout_file(ctsout_txt_file)
    if model_output_file:
        simulation.set_model_stdout(model_output_file)
    simulation.save()
    return simulation

class DownloadViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user")
        self.user.set_password("1")
        self.user.save()
        self.scenario = Scenario.objects.create(
            user=self.user,
            xml=""
        )
        self.client.login(username="user", password="1")

    def test_anonymous(self):
        simulation = create_simulation(self.user, input_file="123")
        client = Client()
        response = client.get(
            reverse("ts_om_viz.download", kwargs={"simulation_id": simulation.id, "name": "input.xml"})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_wrong_user(self):
        user = User.objects.create(username="user1")
        simulation = create_simulation(self.user, input_file="123")
        self.scenario.new_simulation = simulation
        self.scenario.user = user
        self.scenario.save()
        response = self.client.get(
            reverse("ts_om_viz.download", kwargs={"simulation_id": simulation.id, "name": "input.xml"})
        )
        self.assertEqual(response.status_code, 403)

    def test_success_get_scenario_xml_1(self):
        simulation = create_simulation(self.user, input_file="123")
        response = self.client.get(
            reverse("ts_om_viz.download", kwargs={"simulation_id": simulation.id, "name": "scenario.xml"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "123")

    def test_success_get_scenario_xml_2(self):
        simulation = create_simulation(self.user, input_file="123")
        self.scenario.new_simulation = simulation
        self.scenario.save()
        response = self.client.get(
            reverse("ts_om_viz.download", kwargs={"simulation_id": simulation.id, "name": "scenario.xml"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "123")

    def test_success_get_output_txt(self):
        simulation = create_simulation(self.user, output_txt_file="output_txt")
        response = self.client.get(
            reverse("ts_om_viz.download", kwargs={"simulation_id": simulation.id, "name": "output.txt"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "output_txt")

    def test_success_get_ctsout_txt(self):
        simulation = create_simulation(self.user, ctsout_txt_file="ctsout_txt")
        response = self.client.get(
            reverse("ts_om_viz.download", kwargs={"simulation_id": simulation.id, "name": "ctsout.txt"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "ctsout_txt")

    def test_success_get_model_output_txt(self):
        simulation = create_simulation(self.user, model_output_file="model_stdout_stderr_txt")
        response = self.client.get(
            reverse("ts_om_viz.download", kwargs={"simulation_id": simulation.id, "name": "model_stdout_stderr.txt"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "model_stdout_stderr_txt")

    def test_incorrect_filename(self):
        simulation = create_simulation(self.user, model_output_file="model_stdout_stderr_txt")
        self.assertRaises(RuntimeError,
            self.client.get,
            reverse("ts_om_viz.download", kwargs={"simulation_id": simulation.id, "name": "bla"})
        )
