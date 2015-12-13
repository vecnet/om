# Copyright (C) 2015, University of Notre Dame
# All rights reserved
import os
import subprocess
import uuid
import sys
from vecnet.simulation import sim_status
import shutil
import logging

if __name__ == "__main__":
    # This is a code to use this script as a standalone python program
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")
    import django
    django.setup()
# Ignore PEP8 warning, the code above is necessary to use Django models in a standalone script
from data_services.models import SimulationOutputFile, Simulation
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

    xml = simulation.input_files.all()[0].get_contents()
    fp = open(os.path.join(input_dir, "scenario.xml"),"w+")
    fp.write(xml)
    fp.close()
    shutil.copy2(os.path.join(base_dir, "files", "scenario_32.xsd"), os.path.join(input_dir, "scenario_32.xsd"))
    shutil.copy2(os.path.join(base_dir, "files", "densities.csv"), os.path.join(input_dir, "densities.csv"))

    # Run OpenMalaria model
    simulation.status = sim_status.RUNNING_MODEL
    simulation.save()
    input_file_path = os.path.join(input_dir, "scenario.xml")
    stdout = open(os.path.join(input_dir, "stdout.txt"), 'w')
    try:
        logging.debug("Running openmalaria.exe")
        exitcode = subprocess.call("%s -s scenario.xml" % settings.SIM_SERVICE_LOCAL_OM_EXECUTABLE,
                         cwd=input_dir,
                         stdout=stdout,
                         stderr=stdout)
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
                SimulationOutputFile.objects.create_file(contents=stdout_contents,
                                                         simulation=simulation,
                                                         name="stdout.txt")
                logging.debug("stdout.txt saved successfully")
            simulation.status = sim_status.SCRIPT_ERROR
            simulation.save()
            return
    except Exception as e:
        logging.debug(e)
        simulation.status = sim_status.SCRIPT_ERROR
        simulation.save()
        return

    # Load output files
    simulation.status = sim_status.STAGING_OUTPUT
    simulation.save()

    try:
        try:
            fp = open(os.path.join(input_dir, "ctsout.txt"))
            ctsout_contents = fp.read()
            fp.close()
        except IOError:
            logging.warn("No ctsout.txt file")
        else:
            SimulationOutputFile.objects.create_file(contents=ctsout_contents,
                                                     simulation=simulation,
                                                     name="ctsout.txt")
        try:
            fp = open(os.path.join(input_dir, "output.txt"))
            ctsout_contents = fp.read()
            fp.close()
        except IOError:
            logging.warn("No output.txt file")
        else:
            SimulationOutputFile.objects.create_file(contents=ctsout_contents,
                                                     simulation=simulation,
                                                     name="output.txt")

        try:
            fp = open(os.path.join(input_dir, "stdout.txt"))
            stdout_contents = fp.read()
            fp.close()
        except IOError:
            logging.warn("No stdout.txt file")
        else:
            SimulationOutputFile.objects.create_file(contents=stdout_contents,
                                             simulation=simulation,
                                             name="stdout.txt")

        simulation.status = sim_status.SCRIPT_DONE
        simulation.save()

    except Exception as e:
        logging.debug(str(e))

        simulation.status = sim_status.OUTPUT_ERROR
        simulation.save()


if __name__ == "__main__":
    sim_id = int(sys.argv[1])
    simulation = Simulation.objects.get(id=sim_id)
    run(simulation)
