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
from django.urls import reverse
from django.test import TestCase, Client
from website.apps.big_brother.models import TrackingCode


class TrackingCodeViewTest(TestCase):
    def test(self):
        response = self.client.get(reverse("big_brother.track", kwargs={"tracking_code": "aaaaa"}))
        self.assertEqual(response.status_code, 200)
        tracking_code = TrackingCode.objects.all()[0]
        self.assertEqual(tracking_code.code, "aaaaa")

    def test_confirmation_code_no_subject(self):
        client = Client()
        url = reverse("big_brother.track", kwargs={"tracking_code": "123"})
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 95)
        # Tracking code should be created
        tracking_code = TrackingCode.objects.all()[0]
        self.assertEqual(tracking_code.code, "123")
        self.assertEqual(tracking_code.ip, "127.0.0.1")
        self.assertEqual(tracking_code.action, "GET")

    def test_confirmation_code_with_subject(self):
        client = Client()
        url = reverse("big_brother.track", kwargs={"tracking_code": "CODECODE"})
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 95)
        # Tracking code should be created
        tracking_code = TrackingCode.objects.all()[0]
        self.assertEqual(tracking_code.code, "CODECODE")
        self.assertEqual(tracking_code.ip, "127.0.0.1")
        self.assertEqual(tracking_code.action, "GET")

    def test_wrong_invitation_code(self):
        client = Client()
        url = reverse("big_brother.track", kwargs={"tracking_code": "123"})
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 95)
        # Tracking code should be created even though confirmation doesn't exist
        tracking_code = TrackingCode.objects.all()[0]
        self.assertEqual(tracking_code.code, "123")