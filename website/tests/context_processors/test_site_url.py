# Copyright (C) 2016, University of Notre Dame
# All rights reserved
from django.test.testcases import TestCase
from django.test.utils import override_settings
from django.urls.base import reverse


class SiteUrlTest(TestCase):
    @override_settings(SITE_URL="https://om.vecnet.org/")
    def test_anonymous_slash(self):
        response = self.client.get(reverse("login"))
        # There is not context if status code is not 200
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["SITE_URL"], "https://om.vecnet.org")

    @override_settings(SITE_URL="https://om.vecnet.org")
    def test_anonymous_no_slash(self):
        response = self.client.get(reverse("login"))
        # There is not context if status code is not 200
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["SITE_URL"], "https://om.vecnet.org")

    @override_settings(SITE_URL="http://localhost:8000/")
    def test_admin_slash(self):
        self.client.login(username="admin", password="1")
        response = self.client.get(reverse("index"))
        # There is not context if status code is not 200
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["SITE_URL"], "http://localhost:8000")

    @override_settings(SITE_URL="http://127.0.0.1:8000")
    def test_admin_no_slash(self):
        self.client.login(username="admin", password="1")
        response = self.client.get(reverse("index"))
        # There is not context if status code is not 200
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["SITE_URL"], "http://127.0.0.1:8000")
