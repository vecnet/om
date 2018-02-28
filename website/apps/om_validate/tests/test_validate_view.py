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

from django.urls import reverse
from django.test.testcases import TestCase


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")

def get_xml(filename="scenario.xml"):
    with open(os.path.join(DATA_DIR, filename)) as fp:
        xml = fp.read()
    return xml

class ValidateViewTest(TestCase):
    def test_no_errors(self):
        response = self.client.post(reverse("validate"), data=get_xml(), content_type='application/octet-stream')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(json_response["result"], 0)

    def test_validation_schema_error(self):
        response = self.client.post(
            reverse("validate"), data=get_xml("scenario_schema_error.xml"), content_type='application/octet-stream'
        )
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(json_response["result"], -1)
        self.assertIsNotNone(json_response["om_output"])
        self.assertEqual(
            "Element '{http://openmalaria.org/schema/scenario_32}scenario': "
            "Missing child element(s). Expected is one of ( demography, pharmacology ).",
            json_response["om_output"][0]
        )
        self.assertEqual(len(json_response["om_output"]), 1)

    def test_validation_om_error(self):
        response = self.client.post(
            reverse("validate"), data=get_xml("scenario_om_error.xml"), content_type='application/octet-stream'
        )
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(json_response["result"], -1)
        self.assertIsNotNone(json_response["om_output"])
        self.assertIn(
            "Error: Unrecognised survey option: \"nHost11\"",
            json_response["om_output"][1]
        )
        self.assertEqual(len(json_response["om_output"]), 4)
