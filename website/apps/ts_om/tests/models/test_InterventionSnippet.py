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

from website.apps.ts_om.models import InterventionSnippet, InterventionComponent


class InterventionSnippetTest(TestCase):
    def setUp(self):
        self.component = InterventionComponent.objects.create(
            name="Name", tag="123",
        )
        self.intervention_snippet = InterventionSnippet.objects.create(
            name="Snippet", component=self.component, xml="123"
        )

    def test(self):
        self.assertEqual(str(self.intervention_snippet), "Snippet")
