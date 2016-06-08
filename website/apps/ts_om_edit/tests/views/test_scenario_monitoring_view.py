import os
import json

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test.testcases import TestCase
from vecnet.openmalaria.healthsystem import get_prob_from_percentage
from vecnet.openmalaria.scenario import Scenario

from website.apps.ts_om.models import Scenario as ScenarioModel, DemographicsSnippet

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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

    def test_get_entomology_view(self):
        response = self.client.get(reverse("ts_om.entomology", kwargs={"scenario_id": self.model_scenario.id}))

        self.assertEqual(response.status_code, 200)

    def test_post_entomology_view(self):
        scenario = Scenario(self.model_scenario.xml)

        self.assertEqual(scenario.entomology.name, "one species")
        self.assertEqual(scenario.entomology.scaledAnnualEIR, 16)
        self.assertEqual(len(scenario.entomology.vectors), 1)

        vector = scenario.entomology.vectors["gambiae"]
        self.assertEqual(vector.mosquito, "gambiae")
        self.assertEqual(vector.propInfected, 0.078)
        self.assertEqual(vector.propInfectious, 0.015)
        self.assertEqual(vector.seasonality.annualEIR, 1)

        annual_eir = 25
        perc_average_eir = 6
        expected_average_eir = perc_average_eir / 100.0
        perc_human_blood_index = 50
        expected_human_blood_index = perc_human_blood_index / 100.0
        monthly_values = [0.121950947577, 0.150033433731, 0.135783169538, 0.142507307385, 0.12160516792, 0.132069391,
                          0.14132650592, 0.12974214888, 0.10223384536, 0.08159456812, 0.0673589848, 0.08462085352]
        post_data = {
            "form-TOTAL_FORMS": 1,
            "form-INITIAL_FORMS": 1,
            "form-MIN_FORMS": 0,
            "form-MAX_FORMS": 1000,
            "annual_eir": annual_eir,
            "form-0-average_eir": perc_average_eir,
            "form-0-human_blood_index": perc_human_blood_index,
            "form-0-monthly_values": json.dumps(monthly_values),
            "form-0-name": "arabiensis",
        }
        response = self.client.post(reverse("ts_om.entomology", kwargs={"scenario_id": self.model_scenario.id}),
                                    post_data)
        self.assertEqual(response.status_code, 302)

        model_scenario = ScenarioModel.objects.get(id=self.model_scenario.id)
        scenario = Scenario(model_scenario.xml)

        self.assertEqual(scenario.entomology.scaledAnnualEIR, annual_eir)
        self.assertEqual(len(scenario.entomology.vectors), 1)

        self.assertRaises(KeyError, lambda: scenario.entomology.vectors["gambiae"])
        vector = scenario.entomology.vectors["arabiensis"]

        self.assertEqual(vector.mosquito, "arabiensis")
        self.assertEqual(vector.propInfected, 0.078)
        self.assertEqual(vector.propInfectious, 0.015)
        self.assertEqual(vector.seasonality.annualEIR, expected_average_eir)
        self.assertEqual(vector.mosq.mosqHumanBloodIndex, expected_human_blood_index)
        self.assertEqual(vector.seasonality.monthlyValues, monthly_values)

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

    def test_get_deployments_view(self):
        response = self.client.get(reverse("ts_om.deployments", kwargs={"scenario_id": self.model_scenario.id}))

        self.assertEqual(response.status_code, 200)

    def test_post_deployments_view(self):
        scenario = Scenario(self.model_scenario.xml)

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
        scenario = Scenario(model_scenario.xml)

        self.assertEqual(len(scenario.interventions.human.deployments), 1)
        self.assertRaises(IndexError, lambda: scenario.interventions.human.deployments[1])
        deployment = scenario.interventions.human.deployments[0]
        self.assertEqual(deployment.name, "test")
        self.assertEqual(len(deployment.components), 1)
        self.assertEqual(deployment.components[0], "LLIN")
        self.assertEqual(len(deployment.timesteps), 4)
        self.assertEqual(deployment.timesteps[2]["time"], 146)