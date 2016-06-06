import os

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test.testcases import TestCase
from vecnet.openmalaria.healthsystem import get_prob_from_percentage
from vecnet.openmalaria.scenario import Scenario

from website.apps.ts_om.models import Scenario as ScenarioModel, DemographicsSnippet

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ScenarioViewsTest(TestCase):
    fixtures = ["DemographicsSnippets"]

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

    def test_get_healthsystem_view(self):
        response = self.client.get(reverse("ts_om.healthsystem", kwargs={"scenario_id": self.model_scenario.id}))

        self.assertEqual(response.status_code, 200)

    def test_post_healthsystem_view(self):
        scenario = Scenario(self.model_scenario.xml)

        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.name, "Kenya ACT")
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.firstLine, "ACT")
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.secondLine, "QN")
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.pSeekOfficialCareSevere, 0.48)
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.pSeekOfficialCareUncomplicated1, 0.04)
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.pSeekOfficialCareUncomplicated2, 0.04)
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.pSelfTreatUncomplicated, 0.0212)

        perc_total = 20
        perc_formal = 40
        expected_prob_total = get_prob_from_percentage(perc_total)
        expected_prob_formal = get_prob_from_percentage(100-perc_formal)
        post_data = {
            "perc_total_treated": str(perc_total),
            "perc_formal_care": str(perc_formal),
            "first_line_drug": "SP",
        }
        response = self.client.post(reverse("ts_om.healthsystem", kwargs={"scenario_id": self.model_scenario.id}),
                                    post_data)
        self.assertEqual(response.status_code, 302)

        model_scenario = ScenarioModel.objects.get(id=self.model_scenario.id)
        scenario = Scenario(model_scenario.xml)

        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.name, "Kenya ACT")
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.firstLine, "SP")
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.secondLine, "QN")
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.pSeekOfficialCareSevere, 0.48)
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.pSeekOfficialCareUncomplicated1, expected_prob_total)
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.pSeekOfficialCareUncomplicated2, expected_prob_total)
        self.assertEqual(scenario.healthSystem.ImmediateOutcomes.pSelfTreatUncomplicated, expected_prob_formal)
