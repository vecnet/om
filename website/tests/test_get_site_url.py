# Copyright (C) 2016, University of Notre Dame
# All rights reserved

import website
from django.test.testcases import TestCase
from django.test.utils import override_settings


class GetSiteUrlTest(TestCase):
    @override_settings(SITE_URL="https://om.vecnet.org/")
    def test_1(self):
        self.assertEqual(website.get_site_url(), "https://om.vecnet.org")

    @override_settings(SITE_URL="https://om-qa.vecnet.org")
    def test_2(self):
        self.assertEqual(website.get_site_url(), "https://om-qa.vecnet.org")

    @override_settings(SITE_URL="http://127.0.0.1:8000")
    def test_3(self):
        self.assertEqual(website.get_site_url(), "http://127.0.0.1:8000")

    @override_settings(SITE_URL="http://localhost:8000/")
    def test_4(self):
        self.assertEqual(website.get_site_url(), "http://localhost:8000")
