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

from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from website.apps.ts_om.tests.factories import ScenarioFactory, get_xml, UserFactory


class GetScenarioStatusViewTest(TestCase):
    def setUp(self):
        self.scenario = ScenarioFactory(xml=get_xml("default.xml"))
        self.client.login(username=self.scenario.user.username, password="1")
        self.url = reverse("ts_om.status")
        # self.data = {"xml": get_xml("default.xml")}
        self.data = {"scenario_id": self.scenario.id}

    def test_permission(self):
        user = UserFactory()
        client = Client()
        client.login(username=user.username, password="1")
        response = client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 403)

    def test_success(self):
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 200)
        # New scenario
        self.assertEqual(response.content.decode("utf-8"), "\n")
