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