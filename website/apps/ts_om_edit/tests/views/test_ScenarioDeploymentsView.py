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

from django.contrib.auth.models import User
from django.urls import reverse
from website.apps.ts_om.models import Scenario as ScenarioModel
from django.test.testcases import TestCase
import os

from website.apps.ts_om.models import Scenario
import vecnet.openmalaria.scenario
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ScenarioDeploymentsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user")
        self.user.set_password("1")
        self.user.save()
        self.client.login(username="user", password="1")
        xml_filename = os.path.join(BASE_DIR, "files", "group 8 baseline p2.xml")
        self.scenario = Scenario.objects.create(xml=open(xml_filename, "rb").read(), user=self.user)
        self.url = reverse("ts_om.deployments", kwargs={"scenario_id": self.scenario.id})
        with open(xml_filename) as xml_file:
            self.model_scenario = ScenarioModel.objects.create(xml=xml_file.read(), user=self.user)

    def test_continuous_deployment_human_intervention_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("&lt;deploy coverage=&quot;0.0&quot; targetAgeYrs=&quot;0.0833&quot; /&gt;", response.content)

        # Can't really test POST with this approach

    def test_post_deployments_view(self):
        scenario = vecnet.openmalaria.scenario.Scenario(self.model_scenario.xml)

        self.assertEqual(len(scenario.interventions.human.deployments), 3)
        deployment = scenario.interventions.human.deployments[1]
        self.assertEqual(deployment.name, "Nets")
        self.assertEqual(len(deployment.components), 1)
        self.assertEqual(deployment.components[0], "LLIN")
        self.assertEqual(len(deployment.timesteps), 3)
        self.assertEqual(deployment.timesteps[2]["time"], 449)

        post_data = {
            "deployment-TOTAL_FORMS": 1,
            "deployment-INITIAL_FORMS": 0,
            "deployment-MIN_FORMS": 0,
            "deployment-MAX_FORMS": 1000,
            "deployment-0-name": "test",
            "deployment-0-timesteps": "0,73,146,730",
            "deployment-0-coverages": "0.0",
            "deployment-0-components": "LLIN"
        }
        response = self.client.post(reverse("ts_om.deployments", kwargs={"scenario_id": self.model_scenario.id}),
                                    post_data)
        self.assertEqual(response.status_code, 302)

        model_scenario = ScenarioModel.objects.get(id=self.model_scenario.id)
        scenario = vecnet.openmalaria.scenario.Scenario(model_scenario.xml)

        self.assertEqual(len(scenario.interventions.human.deployments), 1)
        self.assertRaises(IndexError, lambda: scenario.interventions.human.deployments[1])
        deployment = scenario.interventions.human.deployments[0]
        self.assertEqual(deployment.name, "test")
        self.assertEqual(len(deployment.components), 1)
        self.assertEqual(deployment.components[0], "LLIN")
        self.assertEqual(len(deployment.timesteps), 4)
        self.assertEqual(deployment.timesteps[2]["time"], 146)
