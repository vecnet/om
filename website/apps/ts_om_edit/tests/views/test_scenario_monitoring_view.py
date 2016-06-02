import os

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test.testcases import TestCase
from vecnet.openmalaria.scenario import Scenario

from website.apps.ts_om.models import Scenario as ScenarioModel


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ScenarioMonitoringViewTest(TestCase):
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

    def test_get_scenario_monitoring_view(self):
        self.assertIsNotNone(self.model_scenario)
        response = self.client.get(reverse("ts_om.monitoring", kwargs={"scenario_id": self.model_scenario.id}))
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
        response = self.client.post(reverse("ts_om.monitoring", kwargs={"scenario_id": self.model_scenario.id}),
                                    post_data)

        self.assertEqual(response.status_code, 302)

        model_scenario = ScenarioModel.objects.get(id=self.model_scenario.id)
        scenario = Scenario(model_scenario.xml)

        self.assertListEqual(scenario.monitoring.SurveyOptions, ["nHost", "nPatent"])
