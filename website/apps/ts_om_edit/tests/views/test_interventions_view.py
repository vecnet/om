import json
import os
import urllib

from django.http import QueryDict
from django.test import TestCase

from website.apps.ts_om_edit.views.ScenarioInterventionsView import parse_parameters, parse_options


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class InterventionsViewTestCast(TestCase):
    post_data = None
    query_dict = None

    def setUp(self):
        json_filename = os.path.join(BASE_DIR, "files", "test_data.json")
        with open(json_filename) as json_file:
            json_data = json.load(json_file)
            self.post_data = json_data["interventions-post-data"]
            query_string = urllib.urlencode(self.post_data)
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
