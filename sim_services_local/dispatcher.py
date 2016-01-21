# Copyright (C) 2015, University of Notre Dame
# All rights reserved
from django.utils import timezone
from django.conf import settings
import subprocess
import sys
import os
from data_services import models as data_models


def submit(simulation_group):
    """
    Run a simulation group on a local machine in background.
    Raises RuntimeError if the submission fails for some reason.
    """
    assert isinstance(simulation_group, data_models.SimulationGroup)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    run_script_filename = os.path.join(base_dir, "run.py")

    for simulation in simulation_group.simulations.all():
        executable = sys.executable
        if hasattr(settings, "PYTHON_EXECUTABLE"):
            executable = settings.PYTHON_EXECUTABLE
        subprocess.Popen(executable + " " + "%s" % run_script_filename + " " + str(simulation.id), shell=True)

    simulation_group.submitted_when = timezone.now()
    simulation_group.save()
