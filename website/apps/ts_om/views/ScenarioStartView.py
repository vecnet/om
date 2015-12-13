from StringIO import StringIO
import json

from django.core.urlresolvers import reverse
from django.views.generic import FormView
from lxml import etree
from lxml.etree import XMLSyntaxError

from website.apps.ts_om.forms import ScenarioStartForm
from ScenarioValidationView import rest_validate
from website.apps.ts_om.models import Scenario, BaselineScenario

__author__ = 'nreed'


class ScenarioStartView(FormView):
    template_name = "ts_om/start.html"
    form_class = ScenarioStartForm
    success_url = "/ts_om/start/"

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

        if form.cleaned_data['choice'] == 'build':
            baseline = BaselineScenario.objects.get(name='Default')
            xml = baseline.xml
        elif form.cleaned_data['choice'] == 'list':
            baseline = form.cleaned_data['list']
            xml = baseline.xml
        elif form.cleaned_data['choice'] == 'upload':
            xml_file = self.request.FILES['xml_file']
            baseline = None

            validation_result = json.loads(rest_validate(xml_file))

            valid = True if (validation_result['result'] == 0) else False

            if not valid:
                self.kwargs['upload_error'] = 'Error: Invalid openmalaria simulation uploaded.'

                return super(ScenarioStartView, self).form_invalid(form)

            xml_file.seek(0)

            xml = xml_file.read()

        name = form.cleaned_data['name']
        desc = form.cleaned_data['desc'] if form.cleaned_data['desc'] != '' else None

        if name:
            try:
                tree = etree.parse(StringIO(str(xml)))
            except XMLSyntaxError:
                pass
            else:
                tree.getroot().set('name', name)
                xml = etree.tostring(tree.getroot(), encoding='UTF-8')

        scenario = Scenario.objects.create(xml=xml, user=self.request.user, description=desc, baseline=baseline)
        scenario.save()

        self.kwargs["scenario_id"] = scenario.id

        return super(ScenarioStartView, self).form_valid(form)
