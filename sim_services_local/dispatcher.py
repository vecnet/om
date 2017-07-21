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

from django.conf import settings
import subprocess
import sys
import os
import logging
from website.apps.ts_om.models import Simulation


logger = logging.getLogger(__name__)


def submit(simulation):
    logger.debug("dispatcher.submit: simulation id %s" % simulation.id)
    assert isinstance(simulation, Simulation)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    executable = sys.executable
    if hasattr(settings, "PYTHON_EXECUTABLE"):
        executable = settings.PYTHON_EXECUTABLE
    run_script_filename = os.path.join(base_dir, "run.py")
    try:
        logger.debug("dispatcher.submit: before Popen")
        p = subprocess.Popen(
            [executable, run_script_filename, str(simulation.id)],
            cwd=base_dir, shell=False
        )
        logger.debug("dispatcher.submit: after Popen")

    except (OSError, IOError) as e:
        logger.exception("subprocess failed: %s", sys.exc_info())
        simulation.status = Simulation.FAILED
        simulation.last_error_message = "Subprocess failed: %s" % e
        simulation.pid = ""
        simulation.save(update_fields=["status", "pid", "last_error_message"])
        return None
    simulation.status = Simulation.QUEUED
    simulation.pid = str(p.pid)
    simulation.last_error_message = ""
    simulation.save(update_fields=["status", "pid", "last_error_message"])
    logger.debug("dispatcher.submit: success, PID: %s" % p.pid)
    return str(p.pid)

