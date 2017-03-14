import json
from xml import etree
from xml.etree import ElementTree

from django.http import HttpResponse

from website.apps.ts_om_edit.forms import ScenarioDemographyForm
from website.apps.ts_om.models import DemographicsSnippet
from website.apps.ts_om_edit.views.ScenarioBaseFormView import ScenarioBaseFormView
from website.apps.ts_om.utils import update_form


class ScenarioDemographyView(ScenarioBaseFormView):
    template_name = "ts_om_edit/demography.html"
    form_class = ScenarioDemographyForm
    next_url = "ts_om.healthsystem"
    prev_url = 'ts_om.monitoring'
    step = "demography"
    om_dict = [
        ("age_dist", "name", "Age distribution"),
        ("human_pop_size", "popSize", "Simulated human population size")
    ]

    # def get_success_url(self):
    #     return reverse('ts_om.healthsystem', kwargs={'scenario_id': self.kwargs['scenario_id']})

    def get_initial(self):
        initial = {"human_pop_size": str(getattr(self.scenario.demography, "popSize", "100"))}

        initial["age_dist"] = name = getattr(self.scenario.demography, "name", "no_name")

        if not DemographicsSnippet.objects.filter(name=name).exists():
            initial["age_dist"] = 'custom'
            self.form_class.base_fields['age_dist'].choices[-1][1]['name'] = 'custom'
            self.form_class.base_fields['age_dist'].choices[-1][1]['title'] = name
            self.form_class.base_fields['age_dist'].choices[-1][1]['xml'] = self.scenario.demography.ageGroup.xml
            self.form_class.base_fields['age_dist'].choices[-1][1]['maximum_age_yrs'] = \
                getattr(self.scenario.demography, "maximumAgeYrs", 0.0)

        initial['age_dist_xml'] = self.scenario.demography.ageGroup.xml
        initial['age_dist_name'] = self.scenario.demography.name

        return initial

    def form_valid(self, form, **kwargs):
        age_dist_name = form.cleaned_data['age_dist_name']
        age_dist_xml = form.cleaned_data['age_dist_xml']

        elem = ElementTree.fromstring(age_dist_xml)

        demography = self.scenario.root.find("demography")

        if demography is None:
            demography = etree.SubElement(self.scenario.root, "demography")

        age_group = demography.find("ageGroup")

        if age_group is not None:
            demography.remove(age_group)

        demography.append(elem)

        self.scenario.demography.name = age_dist_name
        self.scenario.demography.maximumAgeYrs = float(form.cleaned_data['maximum_age_yrs'])

        self.scenario.demography.popSize = form.cleaned_data['human_pop_size']

        return super(ScenarioDemographyView, self).form_valid(form, kwargs={'xml': self.scenario.xml})


def update_demography_form(request, scenario_id):
    data = update_form(request, scenario_id)
    temp_scenario = None

    if "valid" not in data:
        return data

    valid = data["valid"]

    if not valid:
        return data

    if "scenario" in data:
        temp_scenario = data["scenario"]

    form_values = {'valid': valid, 'human_pop_size': temp_scenario.demography.popSize,
                   'age_dist': temp_scenario.demography.name}

    if not DemographicsSnippet.objects.filter(name=temp_scenario.demography.name).exists():
        form_values['name'] = temp_scenario.demography.name
        form_values['title'] = temp_scenario.demography.name
        form_values['xml'] = temp_scenario.demography.ageGroup.xml
        form_values['maximum_age_yrs'] = temp_scenario.demography.maximumAgeYrs

    return HttpResponse(json.dumps(form_values), content_type="application/json")
