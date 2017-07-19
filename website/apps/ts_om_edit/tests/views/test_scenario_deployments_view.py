from django.contrib.auth.models import User
from django.urls import reverse
from django.test.client import Client
from django.test.testcases import TestCase
import os

from website.apps.ts_om.models import Scenario

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ScenarioDeploymentsViewTest(TestCase):
    def test_continuous_deployment_human_intervention_get(self):
        xml_filename = os.path.join(BASE_DIR, "files", "group 8 baseline p2.xml")
        self.client = Client()
        user = User.objects.create(username="user")
        user.set_password("1")
        user.save()
        self.client.login(username="user", password="1")
        response = self.client.get(reverse("ts_om.list"))
        self.assertEqual(response.status_code, 200)
        scenario = Scenario.objects.create(xml=open(xml_filename, "rb").read(), user=user)
        response = self.client.get(reverse("ts_om.deployments", kwargs={"scenario_id": scenario.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn("&lt;deploy coverage=&quot;0.0&quot; targetAgeYrs=&quot;0.0833&quot; /&gt;", response.content)

        # Can't really test POST with this approach
