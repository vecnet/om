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
from django.http import HttpResponse
from django.views.generic import FormView
from vecnet.openmalaria.scenario import Scenario

from website.apps.ts_om.models import Scenario as ScenarioModel
from website.apps.ts_om.views.ScenarioValidationView import rest_validate


from website.notification import set_notification, INFO, DANGER


# https://django.readthedocs.org/en/1.5.x/topics/class-based-views/generic-editing.html
class ScenarioBaseFormView(FormView):
    model_scenario = None
    scenario = None
    next_url = "ts_om.summary2"
    prev_url = None
    step = None

    def get_success_url(self):
        reverse_url = self.request.POST.get('submit', self.next_url)
        return reverse(reverse_url, kwargs={'scenario_id': self.kwargs['scenario_id']})

    def get_context_data(self, **kwargs):
        context = super(ScenarioBaseFormView, self).get_context_data(**kwargs)

        context["xml"] = self.scenario.xml
        context['scenario_id'] = self.model_scenario.id
        context['scenario'] = self.model_scenario
        context['step'] = self.step
        context['prev_url'] = self.prev_url

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
            set_notification(self.request, validation_result, DANGER)
            return super(ScenarioBaseFormView, self).form_invalid(form)

        self.model_scenario.xml = self.scenario.xml

        if not self.request.is_ajax() or json.loads(self.request.POST["save"]):
            if not self.model_scenario.new_simulation:
                self.model_scenario.save()
            else:
                # Don't save scenario if it has been submitted already
                set_notification(self.request, "Not saved", INFO)

        if not self.request.is_ajax():
            return super(ScenarioBaseFormView, self).form_valid(form)
        else:
            data = {
                'xml': kwargs['kwargs']["xml"]
            }

            return self.render_to_json_response(data)
