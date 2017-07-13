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

import os
import subprocess
import uuid
import sys
import shutil
import logging


if __name__ == "__main__":
    # This is a code to use this script as a standalone python program
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings.production")
    import django
    django.setup()
# Ignore PEP8 warning, the code above is necessary to use Django models in a standalone script
from website.apps.ts_om.models import Simulation

from django.conf import settings



def run(simulation):
    assert isinstance(simulation, Simulation)

    # Prepare input files
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = "%s-%s" %(simulation.id, str(uuid.uuid4()))
    if hasattr(settings, "SIM_SERVICE_LOCAL_INPUT_DIR"):
        input_dir = os.path.join(settings.SIM_SERVICE_LOCAL_INPUT_DIR,input_dir)
    os.makedirs(input_dir)
    logging.basicConfig(filename=os.path.join(input_dir, 'error.log'), level=logging.DEBUG)
    logging.debug("Working directory: %s" % input_dir)
    xml = simulation.input_file.read()
    fp = open(os.path.join(input_dir, "scenario.xml"),"w+")
    fp.write(xml)
    fp.close()
    shutil.copy2(os.path.join(base_dir, "sim_services_local", "files", "scenario_32.xsd"), os.path.join(input_dir, "scenario_32.xsd"))
    shutil.copy2(os.path.join(base_dir, "sim_services_local", "files", "densities.csv"), os.path.join(input_dir, "densities.csv"))

    # Run OpenMalaria model
    simulation.status = Simulation.RUNNING
    simulation.cwd = input_dir
    simulation.save(update_fields=["status", "cwd"])
    input_file_path = os.path.join(input_dir, "scenario.xml")
    stdout = open(os.path.join(input_dir, "stdout.txt"), 'w')
    try:
        logging.debug("Running openmalaria.exe")
        exitcode = subprocess.call(
            "%s -s scenario.xml" % settings.SIM_SERVICE_LOCAL_OM_EXECUTABLE,
            shell=True,
            cwd=input_dir,
            stdout=stdout,
            stderr=stdout
        )
        logging.debug("Openmalaria execution complete")
        stdout.flush()
        stdout.close()
        if exitcode != 0:
            logging.debug("Exit code: %s" % exitcode)
            try:
                fp = open(os.path.join(input_dir, "stdout.txt"))
                stdout_contents = fp.read()
                fp.close()
            except IOError:
                logging.warn("No stdout.txt file")
            else:
                logging.debug("Saving stdout.txt")
                simulation.set_model_stdout(stdout_contents)
                logging.debug("stdout.txt saved successfully")
            simulation.status = Simulation.FAILED
            simulation.last_error_message = "Exit code: %s" % exitcode
            simulation.save()
            return
    except Exception as e:
        logging.debug(e)
        simulation.status = Simulation.FAILED
        simulation.last_error_message = "%s" % e
        simulation.save()
        return

    try:
        try:
            fp = open(os.path.join(input_dir, "ctsout.txt"))
            ctsout_contents = fp.read()
            fp.close()
            simulation.set_ctsout_file(ctsout_contents)
        except IOError:
            logging.warn("No ctsout.txt file")

        try:
            with open(os.path.join(input_dir, "output.txt")) as fp:
                simulation.set_output_file(fp)
        except IOError:
            logging.warn("No output.txt file")

        try:
            fp = open(os.path.join(input_dir, "stdout.txt"))
            stdout_contents = fp.read()
            fp.close()
            simulation.set_model_stdout(stdout_contents)
        except IOError:
            logging.warn("No stdout.txt file")

        simulation.status = Simulation.COMPLETE
        simulation.last_error_message = ""
        simulation.save()

    except Exception as e:
        logging.debug(str(e))

        simulation.status = Simulation.FAILED
        simulation.last_error_message = "I/O Error"
        simulation.save()


def main(sim_id):
    simulation = Simulation.objects.get(id=sim_id)
    run(simulation)


if __name__ == "__main__":
    sim_id = int(sys.argv[1])
    main(sim_id)
