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
from io import BytesIO

from django.http.response import HttpResponse
from django.test import TestCase, Client
from django.test.client import RequestFactory
from mock.mock import patch

from website.apps.big_brother.middleware import BigBrotherMiddleware
from website.apps.big_brother.models import PageVisit
from website.apps.ts_om.tests.factories import UserFactory


class TestBigBrotherMiddleware(TestCase):
    def setUp(self):
        self.middleware = BigBrotherMiddleware()

    def test1(self):
        c = Client()
        response = c.get("/")
        page_visit = PageVisit.objects.get(url="/")
        self.assertEqual(page_visit.http_code, "200")
        self.assertIsNone(page_visit.user)
        self.assertEqual(page_visit.url, "/")

    def test_404(self):
        c = Client()
        response = c.get("/sdfsdfdsfsdfds")
        page_visit = PageVisit.objects.get(url="/sdfsdfdsfsdfds")
        self.assertEqual(page_visit.http_code, "404")
        self.assertIsNone(page_visit.user)
        self.assertEqual(page_visit.url, "/sdfsdfdsfsdfds")

    def test_page_visit_post_ascii(self):
        self.client.post("/", data={"file": BytesIO("1234")})
        page_visit = PageVisit.objects.get(url="/")
        # Django test client (as of v1.10) only allows form-encoded data
        # POST content is something like
        # print page_visit.post_content
        # --BoUnDaRyStRiNg
        # Content-Disposition: form-data; name="file"; filename="file"
        # Content-Type: application/octet-stream
        #
        # 1234
        # --BoUnDaRyStRiNg--
        self.assertIn("1234", page_visit.post_content)

    def test_page_visit_post_binary(self):
        data = "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10"
        self.client.post("/", data={"data": BytesIO(data)})
        page_visit = PageVisit.objects.get(url="/")
        # Django test client (as of v1.10) only allows form-encoded data
        # Note that encode('string_escape') in big brother middleware converts \x09 to \t, \0x0a to \n and so on
        self.assertIn(
            "\\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08\\t\\n\\x0b\\x0c\\r\\x0e\\x0f\\x10",
            page_visit.post_content,
        )

    def test_page_visit_post_binary_2(self):
        # content = "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0f\xff"
        content = ""
        for ch in range(0, 256):
            content += chr(ch)
        self.client.post("/", data={"test": BytesIO(content)})
        page_visit = PageVisit.objects.get(url="/")
        # Django test client (as of v1.10) only allows form-encoded data
        # Note that encode('string_escape') in big brother middleware converts \x0a to \t etc
        self.assertIn(
            "\\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08\\t\\n\\x0b\\x0c\\r\\x0e\\x0f\\x10",
            page_visit.post_content,
        )

    @patch("website.apps.big_brother.models.PageVisit.save")
    def test_exception_save(self, save_func):
        save_func.side_effect = Exception("ERROR")
        c = Client()
        response = c.get("/")
        # Make sure the request came through even though we can't save PageVisit
        self.assertEqual(response.status_code, 200)
        # Make sure save() actually failed
        self.assertEqual(PageVisit.objects.filter(url="/").exists(), False)

    @patch("website.apps.big_brother.middleware.PageVisit")
    @patch("website.apps.big_brother.middleware.PageVisit.save")
    def test_exception_save_2(self, save_func, page_visits_class):
        save_func.side_effect = ValueError("PROCESS")
        c = Client()
        response = c.get("/")
        self.assertEqual(response.status_code, 200)

    def test_exception_process_response(self):
        factory = RequestFactory()
        request = factory.get('/')
        page_visit = PageVisit.objects.create(url="/")
        request.page_visit = page_visit
        request.user = UserFactory()
        response = HttpResponse()
        with patch("website.apps.big_brother.middleware.PageVisit.save", side_effect=ValueError("PROCESS2")):
            new_response = BigBrotherMiddleware.process_response(request, response)
        self.assertIsNotNone(response)
        self.assertEqual(response, new_response)
        page_visit.refresh_from_db()
        self.assertEqual(page_visit.http_code, "")
