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

from website.apps.email.models import Email
from website.apps.ts_om.utils import send_daily_report


class SendDailyReportTest(TestCase):
    def setUp(self):
        pass

    def test(self):
        send_daily_report(["alex@example.com"])
        self.assertEqual(Email.objects.count(), 1)
        email = Email.objects.first()
        self.assertEqual(email.email_recipient, "alex@example.com")
        self.assertEqual(email.status, Email.SENT)
