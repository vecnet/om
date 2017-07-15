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

from datetime import timedelta

import website
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.timezone import datetime

from website.apps.email.utils.send_html_email import send_html_email
from website.apps.ts_om.models import Scenario
from website.apps.ts_om.utils import send_daily_report


def get_users_created_yesterday():
    return User.objects.filter(date_joined__date=(datetime.today() - timedelta(days=1)))


def get_scenarios_updated_yesterday():
    return Scenario.objects.filter(last_modified__date=(datetime.today() - timedelta(days=1)))


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--emails", action="store", type=str)

    def handle(self, *args, **options):
        """
        Main function for the management command.
        Send list of new user accounts created yesterday. Should be run from cron 1 minute after midnight
        """
        emails = options["emails"].replace(" ", "").split(",")
        send_daily_report(emails)
