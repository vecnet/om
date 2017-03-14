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
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from data_services.models import SimulationInputFile, SimulationOutputFile, Simulation
from vecnet.openmalaria.output_parser import OutputParser


logger = logging.getLogger(__name__)


def om_output_parser_from_simulation(simulation):
    """

    :param simulation: data_services.models.Simulation object
    :return: vecnet.openmalaria.output_parser.OutputParser generated from simulation
    """
    sim_id = simulation.id

    # Get contents of xml input file and filename (if available)
    if isinstance(simulation, Simulation):
        try:
            scenario_file = SimulationInputFile.objects.filter(simulations=simulation, name="scenario.xml")
            scenario = str(scenario_file[0].get_contents())
        except ObjectDoesNotExist:
            raise TypeError("No scenario.xml file in the simulation %s" % sim_id)
        except MultipleObjectsReturned:
            return TypeError("Multiple scenario.xml files are found in the simulation %s" % sim_id)

        # Get contents of survey output file
        try:
            output = SimulationOutputFile.objects.get(simulation=simulation, name="output.txt")
            output = output.get_contents()
        except ObjectDoesNotExist:
            output = None
        except MultipleObjectsReturned:
            raise TypeError("Multiple output.txt files in Simulation %s" % sim_id)

        # Get contents of continuous output file
        try:
            ctsout = SimulationOutputFile.objects.get(simulation=simulation, name="ctsout.txt")
            ctsout = ctsout.get_contents()
        except ObjectDoesNotExist:
            ctsout = None
        except MultipleObjectsReturned:
            raise TypeError("Multiple cstout.txt files in Simulation %s" % sim_id)

        if output is None and ctsout is None:
            raise TypeError("Error! Both output.txt and ctsout.txt are missing")

        oms = OutputParser(scenario, survey_output_file=output, cts_output_file=ctsout)
        return oms

    try:
        scenario = simulation.input_file.read()
    except Exception as e:
        logger.debug("Exception when executing simulation.input_file.read(): %s" % e)
        raise TypeError("No scenario.xml file in the simulation %s" % sim_id)

    try:
        output = simulation.output_file.read()
    except:
        output = None

    try:
        ctsout = simulation.ctsout_file.read()
    except:
        ctsout = None

    oms = OutputParser(scenario, survey_output_file=output, cts_output_file=ctsout)
    return oms