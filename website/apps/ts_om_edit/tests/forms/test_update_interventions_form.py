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
from django.urls.base import reverse

from website.apps.ts_om.tests.factories import ScenarioFactory
from website.apps.ts_om_edit.tests.views.test_ScenarioSummaryView import get_xml


class UpdateInterventionsFormTest(TestCase):
    def setUp(self):
        self.scenario = ScenarioFactory()
        self.client.login(username=self.scenario.user.username, password="1")
        self.url = reverse("ts_om.interventions.update.form", kwargs={"scenario_id": self.scenario.id})
        self.data = {"xml": get_xml("group 8 baseline p2.xml")}

    def test(self):
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.content, "{'valid': true}")