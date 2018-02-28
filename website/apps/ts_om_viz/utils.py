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
from vecnet.openmalaria.output_parser import OutputParser


logger = logging.getLogger(__name__)


def om_output_parser_from_simulation(simulation):
    """

    :param simulation: website.apps.ts_om.models.Simulation object
    :return: vecnet.openmalaria.output_parser.OutputParser generated from simulation
    """
    sim_id = simulation.id

    # Get contents of xml input file and filename (if available)
    try:
        scenario = simulation.input_file.read().decode("utf-8")
    except Exception as e:
        logger.debug("Exception when executing simulation.input_file.read(): %s" % e)
        raise TypeError("No scenario.xml file in the simulation %s" % sim_id)

    try:
        output = simulation.output_file.read().decode("utf-8")
    except:
        output = None

    try:
        ctsout = simulation.ctsout_file.read().decode("utf-8")
    except:
        ctsout = None

    oms = OutputParser(scenario, survey_output_file=output, cts_output_file=ctsout)
    return oms