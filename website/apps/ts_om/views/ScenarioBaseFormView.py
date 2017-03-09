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
from xml.etree.ElementTree import ParseError
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse

from django.views.generic import FormView
from django.http import HttpResponse
from vecnet.openmalaria.scenario import Scenario

from website.apps.ts_om.views.ScenarioValidationView import rest_validate
from website.apps.ts_om.models import Scenario as ScenarioModel


# https://django.readthedocs.org/en/1.5.x/topics/class-based-views/generic-editing.html
class ScenarioBaseFormView(FormView):
    model_scenario = None
    scenario = None
    next_url = "ts_om.summary2"

    def get_success_url(self):
        reverse_url = self.request.POST.get('submit', self.next_url)
        return reverse(reverse_url, kwargs={'scenario_id': self.kwargs['scenario_id']})

    def get_context_data(self, **kwargs):
        context = super(ScenarioBaseFormView, self).get_context_data(**kwargs)

        context["xml"] = self.scenario.xml
        context['scenario_id'] = self.model_scenario.id
        context['scenario'] = self.model_scenario

        return context

    def get_form(self, form_class):
        if "scenario_id" in self.kwargs:
            scenario_id = self.kwargs["scenario_id"]
            self.model_scenario = ScenarioModel.objects.get(id=scenario_id)

            if self.request.user != self.model_scenario.user:
                raise PermissionDenied

            if "xml" in self.request.POST:
                xml = self.request.POST["xml"]
            else:
                xml = self.model_scenario.xml

            try:
                self.scenario = Scenario(xml)
            except ParseError:
                self.scenario = None

        return super(ScenarioBaseFormView, self).get_form(form_class)

    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        response = super(ScenarioBaseFormView, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response

    def form_valid(self, form, **kwargs):
        validation_result = json.loads(rest_validate(self.scenario.xml))
        valid = True if (validation_result['result'] == 0) else False

        if not valid:
            self.kwargs['validation_error'] = 'Error: Invalid openmalaria xml.'

            return super(ScenarioBaseFormView, self).form_invalid(form)

        self.model_scenario.xml = self.scenario.xml

        if not self.request.is_ajax() or json.loads(self.request.POST["save"]):
            self.model_scenario.save()

        if not self.request.is_ajax():
            return super(ScenarioBaseFormView, self).form_valid(form)
        else:
            data = {
                'xml': kwargs['kwargs']["xml"]
            }

            return self.render_to_json_response(data)

def update_form(request, scenario_id):
    if not request.user.is_authenticated() or not scenario_id or scenario_id < 0:
        return

    xml_file = request.POST['xml']
    json_str = rest_validate(xml_file)
    validation_result = json.loads(json_str)

    valid = True if (validation_result['result'] == 0) else False

    if not valid:
        return HttpResponse(json_str, content_type="application/json")

    model_scenario = ScenarioModel.objects.get(id=scenario_id)
    if model_scenario is None:
        return HttpResponse(json.dumps({'valid': False}), content_type="application/json")

    if request.user != model_scenario.user:
        raise PermissionDenied

    try:
        temp_scenario = Scenario(xml_file)
    except ParseError:
        return HttpResponse(json.dumps({'valid': False}), content_type="application/json")

    return {"valid": valid, "scenario": temp_scenario}
