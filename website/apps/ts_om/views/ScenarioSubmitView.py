import json

from django.http import HttpResponse
from django.views.generic.base import View

from website.apps.ts_om import submit

__author__ = 'nreed'


class ScenarioSubmitView(View):
    def post(self, request):
        simulation = submit.submit(request.user, request.read())

        sim_id = -1

        if simulation:
            sim_id = simulation.id

        data = {'sim_id': sim_id}

        return HttpResponse(json.dumps(data), mimetype="application/json")
