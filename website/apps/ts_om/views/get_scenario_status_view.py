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
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render

from website.apps.ts_om.models import Scenario, Simulation


@login_required
def get_scenario_status_view(request):
    scenario_id = request.POST.get("scenario_id", None)
    scenario = get_object_or_404(Scenario, pk=scenario_id)
    if scenario.user != request.user:
        raise PermissionDenied

    return render(request, "ts_om/scenario_status.html", context={"scenario": scenario})
