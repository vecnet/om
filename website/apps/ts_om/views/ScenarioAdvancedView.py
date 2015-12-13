# Create your views here.
# PEP 0263
# -*- coding: utf-8 -*-
########################################################################################################################
# VECNet CI - Prototype
# Date: 4/5/2013
# Institution: University of Notre Dame
# Primary Authors:
#   Alexander Vyushkov <Alexander.Vyushkov@nd.edu>
#   Nicolas Reed <nreed4@nd.edu>
########################################################################################################################
from xml.etree.ElementTree import ParseError
from django.core.exceptions import PermissionDenied

from django.core.urlresolvers import reverse
from django.views.generic import FormView
from django.views.generic.base import TemplateView
from vecnet.openmalaria.scenario import Scenario
from vecnet.openmalaria.monitoring import get_survey_times

from website.apps.ts_om import submit
from website.apps.ts_om.forms import ScenarioSummaryForm
from website.apps.ts_om.models import Scenario as ScenarioModel
from website.middleware import HttpRedirectException


class ScenarioAdvancedView(TemplateView):
    template_name = "ts_om/advanced.html"

    def post(self, *args, **kwargs):
        scenario_id = self.kwargs["scenario_id"]
        scenario = ScenarioModel.objects.get(id=scenario_id)
        if self.request.user != scenario.user:
            raise PermissionDenied
        scenario.name = self.request.POST.get('name', scenario.name)
        scenario.description = self.request.POST.get('desc', scenario.description)
        scenario.xml = self.request.POST.get('xml', scenario.xml)
        scenario.save()
        if 'run' in self.request.POST:
            # Clicked "Save and Run" button
            # Will submit a` scenario to Simulation Manager here
            pass
        raise HttpRedirectException(reverse('ts_om.list'))

    def get_context_data(self, **kwargs):
        context = super(ScenarioAdvancedView, self).get_context_data(**kwargs)
        scenario_id = self.kwargs["scenario_id"]
        basic_url = self.request.GET.get("basic_url", 'ts_om.summary2')
        self.model_scenario = ScenarioModel.objects.get(id=scenario_id)

        if self.request.user != self.model_scenario.user:
            raise PermissionDenied
        try:
            self.scenario = Scenario(self.model_scenario.xml)
        except ParseError:
            self.scenario = None

        if self.scenario:
            context["scenario"] = self.model_scenario
        context["basic_url"] = reverse(basic_url, kwargs={"scenario_id": scenario_id})

        return context

