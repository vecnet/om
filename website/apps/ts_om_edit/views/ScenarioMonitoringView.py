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
from vecnet.openmalaria.monitoring import get_survey_times, set_survey_times

from website.apps.ts_om_edit.forms import ScenarioMonitoringForm
from website.apps.ts_om_edit.views.ScenarioBaseFormView import ScenarioBaseFormView
from website.apps.ts_om_edit.utils import update_form


class ScenarioMonitoringView(ScenarioBaseFormView):
    template_name = "ts_om_edit/monitoring.html"
    form_class = ScenarioMonitoringForm
    next_url = 'ts_om.demography'
    prev_url = None
    step = 'monitoring'
    om_dict = [
        ("nr_per_age_group", "nHost", "Number of individuals per age group (required)"),
        ("patent_infections", "nPatent", "Patent infections (detected by a test) (recommended)"),
        ("uncomplicated_episodes", "nUncomp", "Uncomplicated episodes (outpatient fever) recommended"),
        ("severe_episodes", "nSevere", "Severe episodes"),
        ("hospitalizations", "nTreatments3", "Hospitalizations"),
        ("direct_deaths", "nDirDeaths", "Direct deaths"),
        ("indirect_deaths", "nIndDeaths", "Indirect deaths"),
        ("itn", "nMassITNs", "ITNs: number of people newly covered"),
        ("irs", "nMassIRS", "IRS: number of people newly covered"),
        ("mda", "nMDAs", "MDA: number of doses given"),
        ("msat", "nMassScreenings", "MSAT: number of people screened"),
        ("vaccine", "nAntibioticTreatments", "Vaccine: number of doses delivered"),
        ("nr_infections", "nNewInfections", "Number of new infections"),
    ]

    # def get_success_url(self):
    #     return reverse('ts_om.demography', kwargs={'scenario_id': self.kwargs['scenario_id']})

    def get_context_data(self, **kwargs):
        context = super(ScenarioMonitoringView, self).get_context_data(**kwargs)

        context["surveys"] = self.scenario.monitoring.surveys

        return context

    def get_initial(self):
        initial = {}

        for o in self.om_dict:
            initial[o[0]] = True if self.scenario.monitoring.SurveyOptions.__contains__(o[1]) else False

        val = self.scenario.monitoring.detectionLimit

        if val == 100 or val == 200 or val == 7:
            initial['parasite_detection_diagnostic_type'] = str(int(val))
        else:
            initial['parasite_detection_diagnostic_type'] = 'custom'

        initial['sim_start_date'] = self.model_scenario.start_date

        monitor_info = get_survey_times(self.scenario.monitoring, self.model_scenario.start_date)

        initial['measure_outputs'] = monitor_info["type"]
        initial['monitor_yrs'] = monitor_info["yrs"]
        initial['monitor_mos'] = monitor_info["mos"]
        initial['monitor_start_date'] = monitor_info["start_date"]

        return initial

    def form_valid(self, form, **kwargs):
        sim_start_date = int(form.cleaned_data['sim_start_date'])
        mon_yrs = int(form.cleaned_data['monitor_yrs'])
        mon_mos = int(form.cleaned_data['monitor_mos'])
        mon_start_date = int(form.cleaned_data['monitor_start_date'])
        output_measurement = form.cleaned_data['measure_outputs']
        diagnostic_type = form.cleaned_data['parasite_detection_diagnostic_type']
        options_list = []

        for o in self.om_dict:
            if unicode(form.cleaned_data[o[0]]).lower() == "true":
                options_list.append(o[1])

        if diagnostic_type != "custom":
            self.scenario.monitoring.detectionLimit = diagnostic_type

        self.scenario.monitoring.SurveyOptions = options_list

        if output_measurement != "custom":
            self.scenario.monitoring.surveys = set_survey_times(sim_start_date, mon_yrs, mon_mos, mon_start_date,
                                                            output_measurement)
        elif "surveys" in self.request.POST and self.request.POST["surveys"] is not None:
            self.scenario.monitoring.surveys = json.loads(self.request.POST["surveys"])

        self.model_scenario.start_date = sim_start_date

        return super(ScenarioMonitoringView, self).form_valid(form, kwargs={'xml': self.scenario.xml})


def update_monitoring_form(request, scenario_id):
    data = update_form(request, scenario_id)
    temp_scenario = None

    if "valid" not in data:
        return data

    valid = data["valid"]

    if not valid:
        return data

    if "scenario" in data:
        temp_scenario = data["scenario"]

    start_date = int(request.POST['start_date'])

    form_values = {'valid': valid}

    for o in ScenarioMonitoringView.om_dict:
        form_values[o[0]] = True if temp_scenario.monitoring.SurveyOptions.__contains__(o[1]) else False

    val = temp_scenario.monitoring.detectionLimit

    if val == 100 or val == 200 or val == 7:
        form_values['parasite_detection_diagnostic_type'] = str(int(val))
    else:
        form_values['parasite_detection_diagnostic_type'] = 'custom'

    form_values['sim_start_date'] = start_date

    monitor_info = get_survey_times(temp_scenario.monitoring, start_date)

    form_values['measure_outputs'] = monitor_info["type"]
    form_values['monitor_yrs'] = monitor_info["yrs"]
    form_values['monitor_mos'] = monitor_info["mos"]
    form_values['monitor_start_date'] = monitor_info["start_date"]
    form_values['surveys'] = json.dumps(temp_scenario.monitoring.surveys)

    return HttpResponse(json.dumps(form_values), content_type="application/json")
