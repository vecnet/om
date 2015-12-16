import requests

from django.conf import settings
from django.http import HttpResponse
from django.views.generic.base import View

from website.apps.ts_om.check import check_url


def rest_validate(f):
    validate_url = check_url(getattr(settings, "TS_OM_VALIDATE_URL", None), "validate")

    response = requests.post(validate_url, data=f)

    return response.text


class ScenarioValidationView(View):
    def post(self, request):
        json_str = rest_validate(request.read())

        return HttpResponse(json_str, content_type="application/json")
