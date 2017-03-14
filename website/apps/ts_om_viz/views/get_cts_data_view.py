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
from vecnet.openmalaria.cts import continuousMeasuresDescription

from website.apps.ts_om.models import Simulation
from website.apps.ts_om_viz.utils import om_output_parser_from_simulation


def get_cts_data_view(request, sim_id, measure_name):
    sim_id = int(sim_id)
    simulation = get_object_or_404(Simulation, id=sim_id)
    if simulation.scenario.user != request.user:
        raise PermissionDenied
    output_parser = om_output_parser_from_simulation(simulation)

    try:
        data = output_parser.cts_output_data[measure_name]
    except KeyError:
        raise Http404("There is no measure %s in simulation %s" % (measure_name, sim_id))
    result = {
        "measure_name": measure_name,
        "sim_id": sim_id,
        "data": data,
        "description": continuousMeasuresDescription.get(measure_name, "")
    }
    return HttpResponse(json.dumps(result), content_type="application/json")