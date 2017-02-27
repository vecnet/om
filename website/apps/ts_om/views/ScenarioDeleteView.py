import json

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from website.apps.ts_om.models import Scenario


class ScenarioDeleteView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ScenarioDeleteView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        data = {'ok': True}

        try:
            scenario_ids = json.loads(request.POST["scenario_ids"])
        except ValueError:
            scenario_ids = []

        if len(scenario_ids) > 0:
            for scenario_id in scenario_ids:
                scenario = Scenario.objects.get(user=request.user, id=scenario_id)

                if scenario:
                    scenario.deleted = not scenario.deleted
                    scenario.save(update_fields=["deleted"])

                else:
                    data['ok'] = False

        return HttpResponse(json.dumps(data), content_type="application/json")
