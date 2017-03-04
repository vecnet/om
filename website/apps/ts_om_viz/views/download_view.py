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
from django.shortcuts import get_object_or_404

from website.apps.ts_om.models import Simulation
from django.core.exceptions import PermissionDenied


@login_required
def download_view(request, simulation_id, name):
    simulation = get_object_or_404(Simulation, id=simulation_id)
    scenario = simulation.scenario
    if scenario and scenario.user != request.user:
        raise PermissionDenied

    filename = name
    content = None
    if filename == "scenario.xml":
        content = simulation.input_file.read()
    elif filename == "output.txt":
        content = simulation.output_file.read()
    elif filename == "ctsout.txt":
        content = simulation.ctsout_file.read()
    elif filename == "model_stdout_stderr.txt":
        content = simulation.model_stdout.read()

    response = HttpResponse(content)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response
