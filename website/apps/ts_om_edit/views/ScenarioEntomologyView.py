import json
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.http import HttpResponse
from vecnet.openmalaria.scenario import Scenario
from vecnet.openmalaria.scenario.interventions import Vaccine

from website.apps.ts_om_edit.forms import ScenarioEntomologyForm, ScenarioEntomologyVectorForm, \
    ScenarioImportedInfectionsForm
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
    step = "entomology"

    # def get_success_url(self):
    #     return reverse('ts_om.interventions', kwargs={'scenario_id': self.kwargs['scenario_id']})

    def get_context_data(self, **kwargs):
        context = super(ScenarioEntomologyView, self).get_context_data(**kwargs)

        context["has_interventions"] = len(self.scenario.interventions.human) or len(
            self.scenario.interventions.vectorPop)

        ScenarioEntomologyVectorFormSet = formset_factory(ScenarioEntomologyVectorForm, extra=0, can_delete=True)

        imported_infection = None
        imported_infection_form = ScenarioImportedInfectionsForm()

        imported_infections = parse_imported_infections(self.scenario)
        if imported_infections:
            imported_infection = imported_infections[0]
            imported_infection_form.initial["name"] = imported_infection["name"]
            imported_infection_form.initial["period"] = imported_infection["period"]
            imported_infection_form.initial["timesteps"] = imported_infection["timesteps"]
            imported_infection_form.initial["values"] = imported_infection["values"]

        context['vector_formset'] = ScenarioEntomologyVectorFormSet(initial=parse_vectors(self.scenario))
        context["has_imported_infection"] = imported_infection is not None
        context["import_infections_form"] = imported_infection_form
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
                    add_to_interventions(self.scenario, vector.mosquito)
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
            remove_vector_from_interventions(self.scenario, vector_name)

        if "has_imported_infection" in self.request.POST and self.request.POST["has_imported_infection"]:
            if self.scenario.interventions.importedInfections is None:
                self.scenario.interventions.add_section("importedInfections")

            name = "Imported Infection"
            if "name" in self.request.POST and self.request.POST["name"] != "":
                name = str(self.request.POST["name"])

            self.scenario.interventions.importedInfections.name = name
            self.scenario.interventions.importedInfections.period = int(self.request.POST["period"])

            rates = []
            timesteps = self.request.POST["timesteps"].split(',')
            values = self.request.POST["values"].split(',')

            for timestep, value in zip(timesteps, values):
                rates.append({
                    "time": timestep,
                    "value": value
                })

            self.scenario.interventions.importedInfections.rates = rates
        else:
            self.scenario.interventions.remove_section("importedInfections")

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

    has_imported_infection = temp_scenario.interventions.importedInfections is not None
    imported_infection = None
    if has_imported_infection:
        imported_infections = parse_imported_infections(temp_scenario)
        if imported_infections:
            imported_infection = imported_infections[0]

    form_values = {
        'valid': valid,
        'annual_eir': temp_scenario.entomology.scaledAnnualEIR,
        'vectors': parse_vectors(temp_scenario),
        'has_interventions': len(temp_scenario.interventions.human) or len(temp_scenario.interventions.vectorPop),
        'has_imported_infection': has_imported_infection,
        'imported_infection': imported_infection
    }

    return HttpResponse(json.dumps(form_values), content_type="application/json")


def add_to_interventions(scenario, vector_name):
    for intervention in scenario.interventions.human:
        if type(intervention) == Vaccine:
            continue

        intervention.add_or_update_anophelesParams({"mosquito": vector_name})

    for intervention in scenario.interventions.vectorPop:
        intervention.add_or_update_anopheles({"mosquito": vector_name})


def remove_vector_from_interventions(scenario, vector_name):
    for intervention in scenario.interventions.human:
        if type(intervention) == Vaccine:
            continue

        intervention.remove_anophelesParams(vector_name)

        if not intervention.anophelesParams:
            try:
                del scenario.interventions.human[intervention.id]
            except KeyError:
                pass

    for intervention in scenario.interventions.vectorPop:
        intervention.remove_anopheles(vector_name)

        if not intervention.anopheles:
            try:
                del scenario.interventions.vectorPop[intervention.name]
            except KeyError:
                pass

def parse_imported_infections(scenario):
    imported_infections = []

    if scenario.interventions.importedInfections is None:
        return imported_infections

    imported_infection = {
        "period": scenario.interventions.importedInfections.period
    }

    name = None
    try:
        name = scenario.interventions.importedInfections.name
    except AttributeError:
        pass

    if name is None or name == "":
        name = "Imported Infection"

    imported_infection["name"] = name
    times = [str(rate["time"]) for rate in scenario.interventions.importedInfections.rates]
    values = [str(rate["value"]) for rate in scenario.interventions.importedInfections.rates]

    imported_infection["timesteps"] = ','.join(times)
    imported_infection["values"] = ','.join(values)

    imported_infections.append(imported_infection)

    return imported_infections
