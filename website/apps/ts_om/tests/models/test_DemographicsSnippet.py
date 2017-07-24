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

from website.apps.ts_om.models import DemographicsSnippet


class DemographicsSnippetTest(TestCase):
    def test(self):
        snippet = DemographicsSnippet.objects.create(
            name="Name", maximum_age_yrs="100", xml="", title="Title", url="",
        )
        self.assertEqual(str(snippet), "Title")
