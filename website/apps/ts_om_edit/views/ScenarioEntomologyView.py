import json
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.http import HttpResponse
from vecnet.openmalaria.scenario import Scenario

from website.apps.ts_om_edit.forms import ScenarioEntomologyForm, ScenarioEntomologyVectorForm
from website.apps.ts_om.models import Scenario as ScenarioModel, AnophelesSnippet
from website.apps.ts_om.views.ScenarioBaseFormView import ScenarioBaseFormView, update_form
from website.middleware import HttpRedirectException
from website.notification import set_notification


@login_required
def delete_species_from_scenario_view(request, scenario_id, species):
    scenario = ScenarioModel.objects.get(id=scenario_id)
    om_scenario = Scenario(scenario.xml)
    del om_scenario.entomology.vectors[species]
    scenario.xml = om_scenario.xml
    scenario.save()
    set_notification(request, "Successfully deleted mosquito %s" % species, "alert-success")
    raise HttpRedirectException(reverse("ts_om.entomology", kwargs={"scenario_id": scenario_id}))


class ScenarioEntomologyView(ScenarioBaseFormView):
    template_name = "ts_om_edit/entomology.html"
    form_class = ScenarioEntomologyForm
    next_url = 'ts_om.interventions'

    # def get_success_url(self):
    #     return reverse('ts_om.interventions', kwargs={'scenario_id': self.kwargs['scenario_id']})

    def get_context_data(self, **kwargs):
        context = super(ScenarioEntomologyView, self).get_context_data(**kwargs)

        context["has_interventions"] = len(self.scenario.interventions.human) or len(
            self.scenario.interventions.vectorPop)

        ScenarioEntomologyVectorFormSet = formset_factory(ScenarioEntomologyVectorForm, extra=0, can_delete=True)

        context['vector_formset'] = ScenarioEntomologyVectorFormSet(initial=parse_vectors(self.scenario))
        context['om_scenario'] = self.scenario

        return context

    def get_initial(self):
        initial = {'annual_eir': self.scenario.entomology.scaledAnnualEIR}

        return initial

    def form_valid(self, form, **kwargs):
        ScenarioEntomologyVectorFormSet = formset_factory(ScenarioEntomologyVectorForm, extra=0, can_delete=True)

        vector_formset = ScenarioEntomologyVectorFormSet(self.request.POST)

        if not vector_formset.is_valid():
            return super(ScenarioEntomologyView, self).form_invalid(form)

        annual_eir = form.cleaned_data["annual_eir"]
        self.scenario.entomology.scaledAnnualEIR = float(annual_eir)

        names = []
        for vector_form in vector_formset:
            name = vector_form.cleaned_data["name"]
            names.append(name)

            try:
                vector = self.scenario.entomology.vectors[name]
            except KeyError:
                xml = None
                for snippet in AnophelesSnippet.objects.all():
                    if snippet.name == name:
                        xml = snippet.anopheles
                        break

                if xml is not None:
                    self.scenario.entomology.vectors.add(xml)
                    vector = self.scenario.entomology.vectors[name]
            finally:
                vector.seasonality.annualEIR = float(vector_form.cleaned_data["average_eir"]) / 100.0
                vector.mosq.mosqHumanBloodIndex = float(vector_form.cleaned_data["human_blood_index"]) / 100.0
                vector.seasonality.monthlyValues = json.loads(vector_form.cleaned_data["monthly_values"])

        vectors_to_delete = []
        for vector in self.scenario.entomology.vectors:
            vector_exists = False
            for name in names:
                if vector.mosquito == name:
                    vector_exists = True
                    break

            if not vector_exists:
                vectors_to_delete.append(vector.mosquito)

        for vector_name in vectors_to_delete:
            del self.scenario.entomology.vectors[vector_name]

        return super(ScenarioEntomologyView, self).form_valid(form, kwargs={'xml': self.scenario.xml})


def parse_vectors(scenario):
    vectors = []
    for vector in scenario.entomology.vectors:
        vectors.append({
            'average_eir': int(round(vector.seasonality.annualEIR * 100, 2)),
            'human_blood_index': int(round(vector.mosq.mosqHumanBloodIndex * 100, 2)),
            'monthly_values': vector.seasonality.monthlyValues,
            'name': vector.mosquito
        })

    return vectors


def update_entomology_form(request, scenario_id):
    data = update_form(request, scenario_id)
    temp_scenario = None

    if "valid" not in data:
        return data

    valid = data["valid"]

    if not valid:
        return data

    if "scenario" in data:
        temp_scenario = data["scenario"]

    form_values = {
        'valid': valid,
        'annual_eir': temp_scenario.entomology.scaledAnnualEIR,
        'vectors': parse_vectors(temp_scenario),
        'has_interventions': len(temp_scenario.interventions.human) or len(temp_scenario.interventions.vectorPop)
    }

    return HttpResponse(json.dumps(form_values), content_type="application/json")
