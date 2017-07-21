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

from django.http import HttpResponse

from website.apps.ts_om.models import Scenario
from website.apps.ts_om.submit import submit
from website.apps.ts_om.views.ScenarioValidationView import rest_validate


def submit_scenarios(request):
    scenarios_data = {"ok": False, "scenarios": []}

    if not request.user.is_authenticated or not "scenario_ids" in request.POST:
        return HttpResponse(json.dumps(scenarios_data), content_type="application/json")

    scenario_ids = json.loads(request.POST["scenario_ids"])

    if scenario_ids is None or len(scenario_ids) <= 0:
        return HttpResponse(json.dumps(scenarios_data), content_type="application/json")

    for scenario_id in scenario_ids:
        scenarios_data["scenarios"].append({"id": scenario_id, "ok": False})

        scenario = Scenario.objects.get(user=request.user, id=int(scenario_id))

        if not scenario or scenario.new_simulation is not None:
            continue

        json_str = rest_validate(scenario.xml)
        validation_result = json.loads(json_str)

        valid = True if (validation_result['result'] == 0) else False

        if not valid:
            continue

        simulation = submit(scenario)

        if simulation:
            # scenario.simulation = simulation
            # scenario.save()
            scenarios_data["ok"] = True

    # scenarios_data["ok"] = True

    return HttpResponse(json.dumps(scenarios_data), content_type="application/json")
