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
from website.apps.ts_om.models import Scenario, Simulation
from website.apps.ts_om.submit import submit_new
import time


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('scenario_id', type=int)
        # Named (optional) arguments
        parser.add_argument(
            "--wait",
            action="store_true",
            dest="wait",
            default=False,
            help="Wait until simulation is complete"
        )

    def handle(self, *args, **options):
        scenario_id = options["scenario_id"]
        scenario = Scenario.objects.filter(pk=scenario_id).first()
        if not scenario:
            print "Scenario %s doesn't exists"
            return
        if scenario.new_simulation:
            print("WARNING: scenario has been submitted already")
        simulation = submit_new(scenario)
        if not simulation:
            print "Can't submit scenario"
            return
        print "Simulation successfully submitted, status: %s" % simulation.status

        if options["wait"]:
            print("Waiting for simulation completion")
            seconds = 0
            while simulation.status not in (Simulation.COMPLETE, Simulation.FAILED):
                time.sleep(1)
                seconds += 1
                if seconds % 30 == 0:
                    print "Waiting %s seconds, status %s" % (seconds, simulation.status)
                # reload model from the database
                simulation.refresh_from_db()
            print "Simulation result: %s" % simulation.status
