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

import logging

from sim_services_local import dispatcher
from website.apps.ts_om.models import Simulation

logger = logging.getLogger(__name__)

def submit(scenario):
    if scenario.new_simulation:
        logger.debug("Scenario %s has been submitted already" % scenario.id)
        return None
    simulation = Simulation.objects.create()
    simulation.set_input_file(scenario.xml)
    try:
        dispatcher.submit(simulation)
        scenario.new_simulation = simulation
        scenario.save(update_fields=["new_simulation"])
        return simulation
    except RuntimeError as e:
        logger.debug("Runtime error in submit: %s" % e)
        return None
