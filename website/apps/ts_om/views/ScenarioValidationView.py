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
import requests
import logging

from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from website.apps.om_validate.views import validate_scenario

from website.apps.ts_om.check import check_url


logger = logging.getLogger(__name__)


@csrf_exempt
def rest_validate(f):
    if f is None:
        return None

    url = getattr(settings, "TS_OM_VALIDATE_URL", None)
    validate_url = None
    if url is not None:
        validate_url = check_url(url, "validate")
    logger.debug("Validation URL: %s" % validate_url)
    if validate_url is not None:
        response = requests.post(validate_url, data=f)

        if response is not None:
            return response.text
    else:
        validation_data = validate_scenario(f)

        if validation_data:
            return json.dumps(validation_data)

    return None

@method_decorator(csrf_exempt, name="dispatch")
class ScenarioValidationView(View):
    def post(self, request):
        json_str = rest_validate(request.read())

        return HttpResponse(json_str, content_type="application/json")
