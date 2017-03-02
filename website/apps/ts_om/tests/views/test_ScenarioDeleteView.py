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
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase

from website.apps.ts_om.models import Scenario


class ScenarioDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user")
        self.user.set_password("1")
        self.user.save()
        self.scenario = Scenario.objects.create(user=self.user, xml="")
        self.data = {"scenario_ids": json.dumps([self.scenario.id])}

    def test_empty_response(self):
        self.client.login(username="user", password="1")
        response = self.client.post(reverse("ts_om.deleteScenario"), data={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '{"ok": false}')
        self.scenario.refresh_from_db()
        self.assertEqual(self.scenario.deleted, False)

    def test_success(self):
        self.client.login(username="user", password="1")
        response = self.client.post(reverse("ts_om.deleteScenario"), data=self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '{"ok": true}')
        self.scenario.refresh_from_db()
        self.assertEqual(self.scenario.deleted, True)

    def test_wrong_user(self):
        user = User.objects.create(username="user1")
        user.set_password("1")
        user.save()
        self.client.login(username="user1", password="1")
        response = self.client.post(reverse("ts_om.deleteScenario"), data=self.data)
        self.assertEqual(response.status_code, 200)
        self.scenario.refresh_from_db()
        self.assertEqual(self.scenario.deleted, False)
        self.assertEqual(response.content, '{"ok": false}')

    def test_no_scenario(self):
        self.client.login(username="user", password="1")
        response = self.client.post(
            reverse("ts_om.deleteScenario"), data={"scenario_ids": json.dumps([1000000])}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '{"ok": false}')
        self.scenario.refresh_from_db()
        self.assertEqual(self.scenario.deleted, False)
