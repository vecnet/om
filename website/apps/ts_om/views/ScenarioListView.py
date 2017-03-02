# PEP 0263tart/
# -*- coding: utf-8 -*-
########################################################################################################################
# VECNet CI - Prototype
# Date: 4/5/2013
# Institution: University of Notre Dame
# Primary Authors:
#   Alexander Vyushkov <Alexander.Vyushkov@nd.edu>
########################################################################################################################
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import ListView
from vecnet.openmalaria.scenario import Scenario
from vecnet.simulation import sim_status

from website.apps.ts_om.models import Scenario as ScenarioModel


class ScenarioListView(ListView):
    template_name = 'ts_om/list.html'
    paginate_by = 10
    model = ScenarioModel

    @method_decorator(ensure_csrf_cookie)
    # Make sure we send CSRF cookie with this view - to ensure that DeleteView is working properly
    def dispatch(self, request, *args, **kwargs):
        return super(ScenarioListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        scenarios = ScenarioModel.objects.filter(user=self.request.user, deleted=False).order_by('-last_modified')

        scenario_sim_list = []

        for s in scenarios:
            try:
                scenario = Scenario(s.xml)
            except:
                continue

            demography_name = getattr(scenario.demography, "name", "no_name")
            version = getattr(scenario, "schemaVersion", None)

            if s.simulation and s.simulation.status == sim_status.SCRIPT_DONE:
                scenario_sim_list.append(
                    (s, "finished", demography_name, version, sim_status.get_description(s.status)))
            elif s.simulation and (s.simulation.status == sim_status.OUTPUT_ERROR or
                                           s.simulation.status == sim_status.SCRIPT_ERROR):
                scenario_sim_list.append((s, "error", demography_name, version, sim_status.get_description(s.status)))
            elif s.simulation:
                scenario_sim_list.append((s, "running", demography_name, version, sim_status.get_description(s.status)))
            else:
                scenario_sim_list.append((s, "", demography_name, version, sim_status.get_description(s.status)))

        return scenario_sim_list

    def get_context_data(self, **kwargs):
        context = super(ScenarioListView, self).get_context_data(**kwargs)

        return context
