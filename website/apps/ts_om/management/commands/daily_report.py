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

from django.core.management.base import BaseCommand
from website.apps.ts_om.utils import send_daily_report



class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--emails", action="store", type=str)

    def handle(self, *args, **options):
        """
        Main function for the management command.
        Send list of new user accounts created yesterday. Should be run from cron 1 minute after midnight
        """
        emails = options["emails"].replace(" ", "").split(",")
        print("Sending report to %s" % emails)
        send_daily_report(emails)
