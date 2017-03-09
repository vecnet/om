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
from django.core.exceptions import PermissionDenied
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404

from website.apps.ts_om.models import Scenario


@login_required
def update_scenario_view(request):
    scenario_id = request.POST["scenario_id"]
    scenario = get_object_or_404(Scenario, id=scenario_id)
    if scenario.user != request.user:
        raise PermissionDenied

    if "xml" in request.POST:
        scenario.xml = request.POST["xml"]
    if "name" in request.POST:
        scenario.name = request.POST["name"]
    if "description" in request.POST:
        scenario.description = request.POST["description"]

    scenario.save()
    return JsonResponse(data={"status": "ok"})
