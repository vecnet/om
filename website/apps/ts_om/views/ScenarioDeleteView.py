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
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from website.apps.ts_om.models import Scenario


class ScenarioDeleteView(View):
    @csrf_exempt
    def post(self, request):
        data = {'ok': False}

        scenario_ids = json.loads(request.POST.get("scenario_ids", "[]"))

        for scenario_id in scenario_ids:
            scenario = Scenario.objects.filter(user=request.user, id=scenario_id).first()

            if scenario:
                scenario.deleted = not scenario.deleted
                scenario.save(update_fields=["deleted"])
                data['ok'] = True

        return HttpResponse(json.dumps(data), content_type="application/json")
