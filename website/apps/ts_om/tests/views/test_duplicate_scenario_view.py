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

import os
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test.testcases import TestCase

from website.apps.ts_om.models import Scenario, BaselineScenario

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


class DuplicateScenarioViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user")
        self.user.set_password("1")
        self.user.save()
        self.client.login(username="user", password="1")
        with open(os.path.join(DATA_DIR, "default.xml")) as fp:
            self.xml = fp.read()
        self.scenario = Scenario.objects.create(
            xml=self.xml,
            user=self.user,
            description="Hey",
            start_date=2007,
            baseline=BaselineScenario.objects.get(name="Default")
        )

    def test_success(self):
        response = self.client.get(reverse("ts_om.duplicate", kwargs={"scenario_id": self.scenario.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Scenario.objects.count(), 2)
        new_scenario = Scenario.objects.all().order_by("id")[1]
        url = reverse('ts_om.summary', kwargs={'scenario_id': new_scenario.id})
        # AssertionError: 'http://testserver/ts_om/5/summary/' != u'/ts_om/5/summary/'
        self.assertIn(url, response.url)
        self.assertEqual(new_scenario.name, "Default scenario - 2")
        # self.assertEqual(new_scenario.xml, self.scenario.xml)
        self.assertEqual(new_scenario.user, self.scenario.user)
        self.assertEqual(new_scenario.description, self.scenario.description)
        self.assertEqual(new_scenario.start_date, self.scenario.start_date)
        self.assertEqual(new_scenario.baseline, self.scenario.baseline)
        self.assertEqual(new_scenario.deleted, False)
        self.assertEqual(new_scenario.is_public, False)
        self.assertEqual(new_scenario.new_simulation, None)

    def test_success_scenario_name_with_number(self):
        self.scenario.name = "Default scenario - 9"
        self.scenario.save()
        response = self.client.get(reverse("ts_om.duplicate", kwargs={"scenario_id": self.scenario.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Scenario.objects.count(), 2)
        new_scenario = Scenario.objects.all().order_by("id")[1]
        url = reverse('ts_om.summary', kwargs={'scenario_id': new_scenario.id})
        # AssertionError: 'http://testserver/ts_om/5/summary/' != u'/ts_om/5/summary/'
        self.assertIn(url, response.url)
        self.assertEqual(new_scenario.name, "Default scenario - 10")

    def test_success_incorrect_xml(self):
        self.scenario.xml="bla-blah"
        self.scenario.baseline=None
        self.scenario.save()
        response = self.client.get(reverse("ts_om.duplicate", kwargs={"scenario_id": self.scenario.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Scenario.objects.count(), 2)
        new_scenario = Scenario.objects.all().order_by("id")[1]
        url = reverse('ts_om.summary', kwargs={'scenario_id': new_scenario.id})
        # AssertionError: 'http://testserver/ts_om/5/summary/' != u'/ts_om/5/summary/'
        self.assertIn(url, response.url)
        self.assertEqual(new_scenario.xml, self.scenario.xml)
        self.assertEqual(new_scenario.description, self.scenario.description)
        self.assertEqual(new_scenario.user, self.scenario.user)
        self.assertEqual(new_scenario.start_date, self.scenario.start_date)
        self.assertEqual(new_scenario.baseline, None)
        self.assertEqual(new_scenario.deleted, False)
        self.assertEqual(new_scenario.is_public, False)
        self.assertEqual(new_scenario.new_simulation, None)

    def test_anonymous(self):
        client = Client()
        self.assertEqual(Scenario.objects.count(), 1)
        response = client.get(reverse("ts_om.duplicate", kwargs={"scenario_id": self.scenario.id}))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
        self.assertEqual(Scenario.objects.count(), 1)

    def test_wrong_user(self):
        client = Client()
        user2 = User.objects.create(username="user2")
        user2.set_password("1")
        user2.save()
        client.login(username="user2", password="1")
        self.assertEqual(Scenario.objects.count(), 1)
        response = client.get(reverse("ts_om.duplicate", kwargs={"scenario_id": self.scenario.id}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Scenario.objects.count(), 1)
