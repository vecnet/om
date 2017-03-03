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

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from data_services.models import Simulation
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied


@login_required
def download_view(request, simulation_id, name):
    simulation = Simulation.objects.get(id=simulation_id)
    if simulation.scenario_set.count() > 0:
        scenario = simulation.scenario_set.all()[0]
        if scenario.user != request.user:
            raise PermissionDenied

    filename = name
    try:
        simulation_file = simulation.input_files.get(name=name)
        filename = simulation_file.metadata.get("filename", filename)
    except ObjectDoesNotExist:
        simulation_file = simulation.simulationoutputfile_set.get(name=name)

    response = HttpResponse(simulation_file.get_contents())
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response