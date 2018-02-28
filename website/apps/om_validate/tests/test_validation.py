import json
import os
from unittest import TestCase

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from website.apps.om_validate.views import validate_view


class ValidationTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_scenario_validation(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files/scenario.xml")) as fp:
            request = self.factory.post("/validate/", data=fp.read(), content_type="text/xml")

        request.user = AnonymousUser()

        response = validate_view(request)

        self.assertEqual(response.status_code, 200)

        json_content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(json_content["result"], 0)
