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
from django.http import HttpResponseRedirect
from django.test.testcases import TestCase

from website.middleware import RedirectionMiddleware, HttpRedirectException


class RedirectionMiddlewareTest(TestCase):
    def setUp(self):
        # Could use RequestFactory if real HttpRequest object is necessary
        self.request = None

    def test_1(self):
        result = RedirectionMiddleware.process_exception(self.request, ValueError)
        self.assertEqual(result, None)

    def test_2(self):
        exc = HttpRedirectException("/")
        result = RedirectionMiddleware.process_exception(self.request, exc)
        self.assertEqual(isinstance(result, HttpResponseRedirect), True)
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.url, "/")
