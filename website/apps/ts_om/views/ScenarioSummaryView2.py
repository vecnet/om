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
from website.apps.ts_om import submit
from website.notification import set_notification


class ScenarioSummaryView2(TemplateView):
    template_name = "ts_om/summary2.html"
    form_class = ScenarioSummaryForm
    model_scenario = None
    scenario = None

    def post(self, *args, **kwargs):
        scenario_id = self.kwargs["scenario_id"]
        scenario = ScenarioModel.objects.get(id=scenario_id)
        if self.request.user != scenario.user:
            raise PermissionDenied
        scenario.name = self.request.POST.get('name', scenario.name)
        scenario.description = self.request.POST.get('desc', scenario.description)
        scenario.save()
        if 'run' in self.request.POST:
            # Clicked "Save and Run" button
            # Will submit a scenario to Simulation Manager here
            simulation = submit.submit(self.request.user, scenario.xml)
            if simulation is None:
                set_notification(self.request, "Can't submit simulation", "alert-danger")
            else:
                scenario.simulation = simulation
                scenario.save()
                set_notification(self.request, "Successfully started simulation", "alert-success")
        raise HttpRedirectException(reverse('ts_om.list'))

    def get_context_data(self, **kwargs):
        context = super(ScenarioSummaryView2, self).get_context_data(**kwargs)
        scenario_id = self.kwargs["scenario_id"]
        self.model_scenario = ScenarioModel.objects.get(id=scenario_id)

        if self.request.user != self.model_scenario.user:
            raise PermissionDenied
        try:
            self.scenario = Scenario(self.model_scenario.xml)
        except ParseError:
            self.scenario = None

        vectors = []

        for v in self.scenario.entomology.vectors:
            vectors.append(v)

        if self.scenario:
            context["scenario"] = self.model_scenario
            context["scenario_id"] = self.model_scenario.id
            context["name"] = self.model_scenario.name
            context["desc"] = self.model_scenario.description if self.model_scenario.description else ""
            context["deleted"] = self.model_scenario.deleted
            context["version"] = self.scenario.schemaVersion

            if self.model_scenario.simulation:
                context['sim_id'] = self.model_scenario.simulation.id

            context["xml"] = self.scenario.xml

            monitor_info = get_survey_times(self.scenario.monitoring, self.model_scenario.start_date)

            context["monitor_type"] = monitor_info["type"]
            context["monitor_yrs"] = monitor_info["yrs"]
            context["monitor_mos"] = monitor_info["mos"]
            context["timesteps"] = monitor_info["timesteps"]

            context["demography"] = self.scenario.demography.name
            context["pop_size"] = self.scenario.demography.popSize

            context["first_line_drug"] = self.scenario.healthSystem.ImmediateOutcomes.firstLine
            context["vectors"] = vectors
            if hasattr(self.scenario.entomology, 'scaledAnnualEIR'):
                context["annual_eir"] = self.scenario.entomology.scaledAnnualEIR
            else:
                context["annual_eir"] = None

            interventions = []
            for component in self.scenario.interventions.human:
                interventions.append(component.id)
            for vectorPop in self.scenario.interventions.vectorPop:
                interventions.append(vectorPop.name)

            context["interventions"] = interventions

        return context

