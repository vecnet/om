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

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from vecnet.openmalaria.cts import continuousMeasuresDescription
from vecnet.openmalaria.output_parser import surveyFileMap

from website.apps.ts_om.models import Simulation
from website.apps.ts_om_viz.utils import om_output_parser_from_simulation
from website.notification import set_notification


class SimulationView(TemplateView):
    template_name = 'ts_om_viz/simulation.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SimulationView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        sim_id = kwargs["id"]

        request = self.request
        if "survey_measure_id" in request.GET and "survey_third_dimension" in request.GET:
            context["survey_measure_id"] = int(request.GET["survey_measure_id"])
            context["survey_third_dimension"] = int(request.GET["survey_third_dimension"])
        context["sim_id"] = sim_id
        simulation = get_object_or_404(Simulation, id=sim_id)
        if simulation.scenario.user != request.user and not request.user.is_superuser:
            raise PermissionDenied
        context["simulation"] = simulation
        # Get contents of xml input file and filename (if available)
        if simulation.input_file:
            context["xml_filename"] = "scenario.xml"

        if simulation.output_file:
            output_txt_filename = "output.txt"
        else:
            output_txt_filename = None

        if simulation.ctsout_file:
            ctsout_txt_filename = "ctsout.txt"
        else:
            ctsout_txt_filename = None


        context["output_txt_filename"] = output_txt_filename
        context["ctsout_txt_filename"] = ctsout_txt_filename
        if simulation.model_stdout:
            context["model_stdout"] = "model_stdout_stderr.txt"

        try:
            output_parser = om_output_parser_from_simulation(simulation)
        except (TypeError, ValueError) as e:
            error_type = "%s" % type(e)
            error_type = error_type.replace("<", "").replace(">", "")
            set_notification(self.request, "Error processing input or output files: (%s) %s" % (error_type, str(e)), 'alert-error')  # noqa
            return context
        try:
            survey_measures = {}
            for measure in output_parser.get_survey_measures():
                # print output_parser.get_survey_measure_name(
                #     measure_id=measure[0], third_dimension=measure[1])
                # measure_key = surveyFileMap[measure[0]][0] + ": " + surveyFileMap[measure[0]][2] + ", ages (" + output_parser.get_survey_measure_name(
                #     measure_id=measure[0], third_dimension=measure[1]) #.split("(")[1]

                measure_name = ""
                if surveyFileMap[measure[0]][1] == "age group":
                    age_group = output_parser.get_monitoring_age_group(measure[1] - 1)
                    age_group_name = "%s - %s" % (age_group["lowerbound"], age_group["upperbound"])
                    measure_name = "(%s)" % age_group_name
                elif surveyFileMap[measure[0]][1] == "vector species":
                    measure_name = "(%s)" % measure[1]
                measure_name = surveyFileMap[measure[0]][0] + ": " + surveyFileMap[measure[0]][2] + measure_name

                survey_measures[measure_name] = measure
        except AttributeError:
            survey_measures = {}
        try:
            cts_measures = {}
            for measure in output_parser.get_cts_measures():
                cts_measures[measure] = continuousMeasuresDescription.get(measure, "").split(".")[0]
        except AttributeError:
            cts_measures = {}

        context["survey_measures"] = survey_measures
        context["cts_measures"] = cts_measures
        context["request"] = request
        return context
