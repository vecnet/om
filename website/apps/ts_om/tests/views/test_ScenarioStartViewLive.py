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

import io

import requests
from django.urls import reverse
from django.test.testcases import LiveServerTestCase
from django.test.utils import override_settings
from lxml import html

from website.apps.ts_om.models import Scenario
from website.apps.ts_om.tests.factories import UserFactory, get_xml


class ScenarioStartViewTestLive(LiveServerTestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.login(username=self.user.username, password="1")
        self.sessionid = self.client.cookies['sessionid']
        self.cookies = {"sessionid": str(self.sessionid.value)}
        self.url = self.live_server_url + reverse("ts_om.start")

    def test_get(self):
        response = requests.get(self.url, cookies=self.cookies)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Please sign in", response.content.decode("utf-8"))
        self.assertIn("<h3>Start new simulation</h3>", response.content.decode("utf-8"))
        self.assertEqual(response.status_code, 200)

    @override_settings(TS_OM_VALIDATE_URL=None)
    def test_post_upload_xml_local_validation(self):
        # We don't have to do it this way, but this is a good example for LiveServerTestCase
        # (test_post_upload_xml_rest_validation does require LiveServerTestCase)
        from django.conf import settings
        xml = get_xml('tororo.xml')
        # Get CSRF token
        response = requests.get(self.url, cookies=self.cookies, allow_redirects=False,)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Please sign in", response.content.decode("utf-8"))
        self.assertIn("<h3>Start new simulation</h3>", response.content.decode("utf-8"))
        tree = html.fromstring(response.content)
        csrf_token_input_element = tree.xpath('//input[@name="csrfmiddlewaretoken"]')[0]
        csrf_token = csrf_token_input_element.value
        self.cookies["csrftoken"] = csrf_token

        # Post the xml + CSRF token
        response = requests.post(
            self.url,
            data={'name': 'Brave New', 'desc': 'Brave New S', 'choice': 'upload', 'csrfmiddlewaretoken': csrf_token},
            files={'xml_file': io.StringIO(xml)},
            cookies=self.cookies,
            allow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        scenario = Scenario.objects.get(description="Brave New S")
        self.assertIn(reverse('ts_om.monitoring', kwargs={'scenario_id': scenario.id}), response.headers['Location'])
        self.assertEqual(scenario.name, "Brave New")
        self.assertIsNone(scenario.new_simulation)
        self.assertEqual(scenario.user, self.user)
        self.assertEqual(scenario.baseline, None)
        self.assertIn("Tororo", scenario.xml)

    def test_post_upload_xml_rest_validation(self):
        with self.settings(TS_OM_VALIDATE_URL=self.live_server_url + reverse("validate")):
            # Note we can't use POST request to live server, because of issue #20238
            # https://code.djangoproject.com/ticket/20238
            # It is fixed in Django 2.0, but until then we can't make a POST inside a POST
            # So using a combination of TestClient and POST
            xml = get_xml('tororo.xml')
            response = self.client.post(
                self.url,
                data={'name': 'Brave New', 'desc': 'Brave New S', 'choice': 'upload',
                      'xml_file': io.StringIO(xml)}
            )
            self.assertEqual(response.status_code, 302)
            scenario = Scenario.objects.get(description="Brave New S")
            self.assertIn(reverse('ts_om.monitoring', kwargs={'scenario_id': scenario.id}), response.url)
            self.assertEqual(scenario.name, "Brave New")
            self.assertIsNone(scenario.new_simulation)
            self.assertEqual(scenario.user, self.user)
            self.assertEqual(scenario.baseline, None)
