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

from django.urls import reverse
from django.views.generic import FormView

from ScenarioValidationView import rest_validate
from website.apps.ts_om.forms import ScenarioStartForm
from website.apps.ts_om.models import Scenario, BaselineScenario


class ScenarioStartView(FormView):
    template_name = "ts_om/start.html"
    form_class = ScenarioStartForm

    def get_success_url(self):
        return reverse('ts_om.monitoring', kwargs={'scenario_id': self.kwargs['scenario_id']})

    def get_context_data(self, **kwargs):
        context = super(ScenarioStartView, self).get_context_data(**kwargs)

        context['scenario_id'] = 0

        if 'upload_error' in self.kwargs:
            context['upload_error'] = self.kwargs['upload_error']

        return context

    def form_invalid(self, form):
        return super(ScenarioStartView, self).form_invalid(form)

    def form_valid(self, form):
        xml = None
        baseline = None

        if form.cleaned_data['choice'] == 'upload' or 'xml_file' in self.request.FILES:
            xml_file = self.request.FILES['xml_file']
            baseline = None
            xml = xml_file.read()
            validation_result = json.loads(rest_validate(xml))

            valid = True if (validation_result['result'] == 0) else False

            if not valid:
                self.kwargs['upload_error'] = 'Error: Invalid openmalaria simulation uploaded.'

                return super(ScenarioStartView, self).form_invalid(form)

        elif form.cleaned_data['choice'] == 'build':
            baseline = BaselineScenario.objects.get(name='Default')
            xml = baseline.xml
        elif form.cleaned_data['choice'] == 'list':
            baseline = form.cleaned_data['list']
            if not baseline:
                self.kwargs['upload_error'] = 'Error: Please specify baseline'
                return super(ScenarioStartView, self).form_invalid(form)

            xml = baseline.xml


        name = form.cleaned_data['name']
        desc = form.cleaned_data['desc'] if form.cleaned_data['desc'] != '' else None

        scenario = Scenario.objects.create(
            name=name, xml=xml, user=self.request.user, description=desc, baseline=baseline
        )
        scenario.save()

        self.kwargs["scenario_id"] = scenario.id

        return super(ScenarioStartView, self).form_valid(form)
