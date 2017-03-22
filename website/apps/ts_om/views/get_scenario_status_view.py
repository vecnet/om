# Copyright (C) 2016, University of Notre Dame
# All rights reserved
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
