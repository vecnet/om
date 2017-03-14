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

import json

from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from vecnet.openmalaria.output_parser import surveyFileMap

from website.apps.ts_om.models import Simulation
from website.apps.ts_om_viz.utils import om_output_parser_from_simulation


def get_survey_data_view(request, sim_id, measure_id, bin_number):
    sim_id = int(sim_id)
    measure_id = int(measure_id)
    try:
        bin_number = int(bin_number)
    except ValueError:
        # Treat bin_number as species name
        pass
    simulation = get_object_or_404(Simulation, id=sim_id)
    if simulation.scenario.user != request.user:
        raise PermissionDenied

    output_parser = om_output_parser_from_simulation(simulation)
    try:
        data = output_parser.survey_output_data[(measure_id, bin_number,)]
    except KeyError:
        raise Http404("There is not measure (%s,%s) in simulation %s" % (measure_id, bin_number, sim_id))

    # Timesteps in years.
    for list_data in data:
        list_data[0] /= 73.0

    # Remove first data point if it is not allCauseIMR
    if measure_id != 21:
        data = data[1:]
    # Include measure_name and sim_id to http response for debug purpose
    result = {"measure_name": output_parser.get_survey_measure_name(measure_id=measure_id, third_dimension=bin_number),
              "sim_id": sim_id,
              "data": data,
              "description": surveyFileMap[measure_id][2]}
    return HttpResponse(json.dumps(result), content_type="application/json")