# Copyright (C) 2016, University of Notre Dame
# All rights reserved
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from website.apps.ts_om.utils import update_form


@csrf_exempt
def update_summary_form(request, scenario_id):
    data = update_form(request, scenario_id)
    temp_scenario = None

    if "valid" not in data:
        return data

    valid = data["valid"]

    if not valid:
        return data

    if "scenario" in data:
        temp_scenario = data["scenario"]

    form_values = {'valid': valid, 'name': temp_scenario.name}

    return JsonResponse(form_values)