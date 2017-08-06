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
from django.test.testcases import TestCase

from website.apps.ts_om.models import ModelSnippet


class ModelSnippetTest(TestCase):
    def test(self):
        model_snippet = ModelSnippet.objects.create(name="R0132", xml="123")
        self.assertEqual(str(model_snippet), "R0132")
