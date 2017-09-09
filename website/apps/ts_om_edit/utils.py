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
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from vecnet.openmalaria.scenario import Scenario

from website.apps.ts_om.models import Scenario as ScenarioModel
from website.apps.ts_om.views.ScenarioValidationView import rest_validate


def update_form(request, scenario_id):
    if not request.user.is_authenticated:
        raise PermissionDenied

    xml_file = request.POST['xml']
    json_str = rest_validate(xml_file)
    validation_result = json.loads(json_str)

    valid = True if (validation_result['result'] == 0) else False

    if not valid:
        return HttpResponse(json_str, content_type="application/json")

    model_scenario = get_object_or_404(ScenarioModel, id=scenario_id)

    if request.user != model_scenario.user:
        raise PermissionDenied

    temp_scenario = Scenario(xml_file)

    return {"valid": valid, "scenario": temp_scenario}
