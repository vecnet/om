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
from django.core.management import call_command
from django.test import TestCase

from website.apps.email.models import Email


class DailyReportTest(TestCase):
    def setUp(self):
        pass

    def test(self):
        call_command("daily_report", emails="alex1@example.com,alex2@example.com")
        self.assertEqual(Email.objects.count(), 2)
        email1 = Email.objects.get(email_recipient="alex1@example.com")
        self.assertEqual(email1.status, Email.SENT)
        email2 = Email.objects.get(email_recipient="alex2@example.com")
        self.assertEqual(email2.status, Email.SENT)
