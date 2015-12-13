import os

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse


class UploadExperimentTest(TestCase):
    def test_invalid_form(self):
        c = Client()

    def test_valid_form(self):
        c = Client()
        f = open(os.path.join(os.path.dirname(__file__), 'scenarios.zip'), 'rb')
        kwargs = {'file': f}
        response = c.post(reverse('ts_om.upload'), kwargs)
        self.assertEqual(200, response.status_code)
