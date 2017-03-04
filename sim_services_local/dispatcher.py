# Copyright (C) 2015, University of Notre Dame
# All rights reserved
from django.utils import timezone
from django.conf import settings
import subprocess
import sys
import os
import logging
from data_services import models as data_models
from website.apps.ts_om.models import Simulation


logger = logging.getLogger(__name__)


def submit_new(simulation):
    logger.debug("submit_new: simulation id %s" % simulation.id)
    assert isinstance(simulation, Simulation)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    executable = sys.executable
    if hasattr(settings, "PYTHON_EXECUTABLE"):
        executable = settings.PYTHON_EXECUTABLE
    run_script_filename = os.path.join(base_dir, "run_new.py")
    try:
        logger.debug("submit_new: before Popen")
        p = subprocess.Popen(
            [executable, run_script_filename, str(simulation.id)],
            cwd=base_dir, shell=False
        )
        logger.debug("submit_new: after Popen")

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
    logger.debug("submit_new: success, PID: %s" % p.pid)
    return str(p.pid)

def submit(simulation_group):
    """
    Run a simulation group on a local machine in background.
    Raises RuntimeError if the submission fails for some reason.
    """
    assert isinstance(simulation_group, data_models.SimulationGroup)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    run_script_filename = os.path.join(base_dir, "run.py")

    for simulation in simulation_group.simulations.all():
        executable = sys.executable
        if hasattr(settings, "PYTHON_EXECUTABLE"):
            executable = settings.PYTHON_EXECUTABLE
        subprocess.Popen(executable + " " + "%s" % run_script_filename + " " + str(simulation.id),
                         cwd=base_dir,
                         shell=True)

    simulation_group.submitted_when = timezone.now()
    simulation_group.save()
