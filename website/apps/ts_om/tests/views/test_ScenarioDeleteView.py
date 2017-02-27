# Copyright (C) 2016, University of Notre Dame
# All rights reserved
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase

from website.apps.ts_om.models import Scenario


class ScenarioDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user")
        self.user.set_password("1")
        self.user.save()
        self.client.login(username="user", password="1")
        self.scenario = Scenario.objects.create(user=self.user)

    def test_sucess(self):
        response = self.client.post(reverse("ts_om.deleteScenario"), data={"scenario_ids":"[%s]" % self.scenario.id})
        self.assertEqual(response.status_code, 200)
        self.scenario.refresh_from_db()
        self.assertEqual(self.scenario.deleted, True)
