import json

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.base import View

from website.apps.ts_om import submit
from website.apps.ts_om.models import Scenario
from website.notification import set_notification, DANGER, SUCCESS


class ScenarioSubmitNewView(View):
    def get(self, request, scenario_id):
        scenario = get_object_or_404(Scenario, id=scenario_id, user=request.user)
        simulation = submit.submit_new(scenario)
        if not simulation:
            set_notification(request, "Can't submit scenario", DANGER)
        else:
            set_notification(request, "Successfully submitted scenario", SUCCESS)

        return HttpResponseRedirect(reverse("ts_om.summary2", kwargs={"scenario_id": scenario_id}))
