import json
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError
from functools import partial, wraps

from django.core.exceptions import PermissionDenied
from django.forms.formsets import formset_factory
from django.http import HttpResponse
from django.template.loader import render_to_string
from vecnet.openmalaria.scenario import Scenario
from vecnet.openmalaria.scenario.interventions import GVI, MDA, Vaccine, VectorPopIntervention

from website.apps.ts_om_edit.forms import ScenarioInterventionsForm, ScenarioGviInterventionForm, \
    ScenarioLarvicidingInterventionForm, ScenarioMdaInterventionForm, ScenarioVaccineInterventionForm, \
    ScenarioImportedInfectionsForm
from website.apps.ts_om.models import Scenario as ScenarioModel, InterventionSnippet
from website.apps.ts_om.views.ScenarioBaseFormView import ScenarioBaseFormView
from website.apps.ts_om.views.ScenarioValidationView import rest_validate
import logging
logger = logging.getLogger(__name__)


class ScenarioInterventionsView(ScenarioBaseFormView):
    template_name = "ts_om_edit/interventions.html"
    form_class = ScenarioInterventionsForm
    next_url = 'ts_om.deployments'

    # def get_success_url(self):
    #     return reverse('ts_om.deployments', kwargs={'scenario_id': self.kwargs['scenario_id']})

    def get_context_data(self, **kwargs):
        context = super(ScenarioInterventionsView, self).get_context_data(**kwargs)

        extra_data = load_interventions_data(self.scenario)

        new_context = context.copy()
        new_context.update(extra_data)

        return new_context

    def form_valid(self, form, **kwargs):
        logger.info("Intervention form valid")
        gvi_vectors = parse_parameters(self.request.POST, "gvi")
        larviciding_vectors = parse_parameters(self.request.POST, "intervention")
        mda_options = parse_options(self.request.POST, "mda")

        ScenarioGviInterventionFormSet = formset_factory(wraps(ScenarioGviInterventionForm)
                                                         (partial(ScenarioGviInterventionForm, vectors=gvi_vectors)),
                                                         extra=0, can_delete=True)
        ScenarioLarvicidingInterventionFormSet = formset_factory(wraps(ScenarioLarvicidingInterventionForm)
                                                                 (partial(ScenarioLarvicidingInterventionForm,
                                                                          vectors=larviciding_vectors)), extra=0,
                                                                 can_delete=True)
        ScenarioMdaInterventionFormSet = formset_factory(wraps(ScenarioMdaInterventionForm)
                                                         (partial(ScenarioMdaInterventionForm, options=mda_options)),
                                                         extra=0, can_delete=True)
        ScenarioVaccineInterventionFormSet = formset_factory(ScenarioVaccineInterventionForm, extra=0, can_delete=True)
        ScenarioImportedInfectionsFormSet = formset_factory(ScenarioImportedInfectionsForm, extra=0, can_delete=True)

        formsets = [
            ScenarioGviInterventionFormSet(self.request.POST, prefix='gvi'),
            ScenarioLarvicidingInterventionFormSet(self.request.POST, prefix='intervention'),
            ScenarioMdaInterventionFormSet(self.request.POST, prefix='mda'),
            ScenarioVaccineInterventionFormSet(self.request.POST, prefix='vaccine'),
            ScenarioImportedInfectionsFormSet(self.request.POST, prefix='importedinfections')
        ]
        logger.debug(formsets)
        for formset in formsets:
            if not formset.is_valid():
                logger.debug("Formset is invalid, " % formset.errors)
                return super(ScenarioInterventionsView, self).form_invalid(form)

        logger.debug("Interventions - all formsets are valid")
        human_intervention_ids = []
        vectorpop_intervention_names = []
        has_imported_infection = False

        for formset in formsets:
            for index, form in enumerate(formset):
                intervention_id = None

                if 'id' in form.cleaned_data:
                    intervention_id = form.cleaned_data['id']

                name = str(form.cleaned_data['name'])
                intervention = None

                if intervention_id is not None:
                    human_intervention_ids.append(intervention_id)

                    try:
                        intervention = self.scenario.interventions.human[intervention_id]
                    except KeyError:
                        component_tag = formset.prefix

                        if component_tag == "vaccine":
                            component_tag = name

                        possible_snippets = InterventionSnippet.objects.filter(component__tag__iexact=component_tag)
                        if possible_snippets is not None:
                            snippet = possible_snippets.get(name=name)

                            if snippet is None:
                                if formset.prefix == "gvi":
                                    snippet = possible_snippets.get(name="GVI")
                                elif formset.prefix == "mda":
                                    snippet = possible_snippets.get(name="Coarthem")
                                elif formset.prefix == "vaccine":
                                    snippet = possible_snippets.get(name="BSV")

                            xml = snippet.xml

                            if len(self.scenario.interventions.human) == 0:
                                self.scenario.interventions.add_section("human")

                            self.scenario.interventions.human.add(xml, id=intervention_id)
                            intervention = self.scenario.interventions.human[intervention_id]
                            intervention.anophelesParams = []
                    finally:
                        if intervention is None:
                            return super(ScenarioInterventionsView, self).form_invalid(form)

                        intervention.name = name

                        if formset.prefix == "gvi" and 'attrition' in form.cleaned_data:
                            intervention.decay.L = float(form.cleaned_data['attrition'])
                            temp_vectors = parse_parameters(self.request.POST, formset.prefix, index=index)
                            for vector in temp_vectors:
                                intervention.add_or_update_anophelesParams(vector)
                        elif formset.prefix == "mda":
                            temp_options = parse_options(self.request.POST, formset.prefix, option_type="option",
                                                         index=index)
                            for option in temp_options:
                                intervention.add_or_update_treatment_option(option)
                        elif formset.prefix == "vaccine":
                            intervention.decay.L = float(form.cleaned_data["attrition"])
                            intervention.efficacyB = float(form.cleaned_data["efficacy_b"])
                            intervention.initialEfficacy = form.cleaned_data["initial_efficacy"].split(',')
                else:
                    if formset.prefix == 'intervention':
                        vectorpop_intervention_names.append(name)

                        try:
                            intervention = self.scenario.interventions.vectorPop[name]
                        except KeyError:
                            possible_snippets = InterventionSnippet.objects.filter(
                                component__tag__iexact=formset.prefix)
                            if possible_snippets is not None:
                                snippet = possible_snippets.get(name="Larviciding")

                                xml = snippet.xml

                                if len(self.scenario.interventions.vectorPop) == 0:
                                    self.scenario.interventions.add_section("vectorPop")

                                self.scenario.interventions.vectorPop.add(xml, name=name)
                                intervention = self.scenario.interventions.vectorPop[name]
                                intervention.anopheles = []
                        finally:
                            intervention.emergenceReduction = float(form.cleaned_data["emergence_reduction"])
                            temp_vectors = parse_parameters(self.request.POST, formset.prefix, index=index)
                            for vector in temp_vectors:
                                intervention.add_or_update_anopheles(vector)
                    elif formset.prefix == 'importedinfections':
                        has_imported_infection = True
                        if self.scenario.interventions.importedInfections is None:
                            self.scenario.interventions.add_section("importedInfections")

                        self.scenario.interventions.importedInfections.name = str(form.cleaned_data["name"])
                        self.scenario.interventions.importedInfections.period = int(form.cleaned_data["period"])

                        rates = []
                        timesteps = form.cleaned_data["timesteps"].split(',')
                        values = form.cleaned_data["values"].split(',')

                        for timestep, value in zip(timesteps, values):
                            rates.append({
                                "time": timestep,
                                "value": value
                            })

                        self.scenario.interventions.importedInfections.rates = rates

        for intervention in self.scenario.interventions.human:
            if intervention.id not in human_intervention_ids:
                try:
                    del self.scenario.interventions.human[intervention.id]
                except KeyError:
                    pass
        for intervention in self.scenario.interventions.vectorPop:
            if intervention.name not in vectorpop_intervention_names:
                try:
                    del self.scenario.interventions.vectorPop[intervention.name]
                except KeyError:
                    pass

        if len(self.scenario.interventions.human) == 0:
            self.scenario.interventions.remove_section("human")
        if len(self.scenario.interventions.vectorPop) == 0:
            self.scenario.interventions.remove_section("vectorPop")
        if not has_imported_infection:
            self.scenario.interventions.remove_section("importedInfections")

        return super(ScenarioInterventionsView, self).form_valid(form, kwargs={'xml': self.scenario.xml})


def parse_initial_vectors(interventions):
    gvi_vectors = []
    for intervention in interventions:
        gvi_vectors.append(intervention['vectors'])

    return gvi_vectors


def parse_gvi_interventions(scenario):
    interventions = []

    for component in scenario.interventions.human:
        if type(component) == GVI:
            component_info = {'attrition': component.decay.L, 'deploy': False, 'coverage': 0, 'timesteps': 0,
                              'id': component.id, 'name': component.name}

            vectors = []

            try:
                component_anopheles_params = component.anophelesParams
            except AttributeError:
                component_anopheles_params = []

            for anopheles in component_anopheles_params:
                vector_info = {
                    'mosquito': anopheles.mosquito,
                    'propActive': anopheles.propActive,
                    'deterrency': anopheles.deterrency,
                    'preprandialKillingEffect': anopheles.preprandialKillingEffect,
                    'postprandialKillingEffect': anopheles.postprandialKillingEffect
                }

                vectors.append(vector_info)

            component_info["vectors"] = vectors
            interventions.append(component_info)

    return interventions


def parse_parameters(post_data, prefix, parameter_type="vector", index=0):
    temp_vectors = []
    for key, value in post_data.iteritems():
        if key.__contains__(prefix) and key.__contains__(parameter_type) \
                and not key.__contains__("inner-prefix"):
            split_key_strings = key.split('-')
            form_index = int(split_key_strings[1])

            if form_index != index:
                continue

            vector_key_string = split_key_strings[2]
            split_vector_key_strings = vector_key_string.split('_', 2)
            vector_index = split_vector_key_strings[1]
            vector_parameter_key = split_vector_key_strings[2]

            found = False
            for temp_vector in temp_vectors:
                if temp_vector[0] == vector_index:
                    temp_vector[1][vector_parameter_key] = value
                    found = True
                    break

            if not found:
                temp_vectors.append((vector_index, {vector_parameter_key: value}))

    return [temp_vector[1] for temp_vector in sorted(temp_vectors, key=lambda temp: temp[0])]


def parse_options(post_data, prefix, option_type="option", index=0):
    temp_vectors = []
    for key, value in post_data.iteritems():
        if key.__contains__(prefix) and key.__contains__(option_type) \
                and not key.__contains__("inner-prefix"):
            split_key_strings = key.split('-')
            form_index = int(split_key_strings[1])

            if form_index != index:
                continue

            vector_key_string = split_key_strings[2]
            split_vector_key_strings = vector_key_string.split('_', 2)
            vector_index = split_vector_key_strings[1]
            vector_parameter_key = split_vector_key_strings[2]

            found = False
            for temp_vector in temp_vectors:
                if temp_vector[0] == vector_index:
                    split_sub_key_strings = vector_parameter_key.split('_')
                    if len(split_sub_key_strings) > 1:
                        sub_parameter_key = split_sub_key_strings[0]
                        sub_parameter_index = int(split_sub_key_strings[1])
                        sub_parameter_sub_key = split_sub_key_strings[2]

                        sub_parameter_key += "s"

                        if sub_parameter_key not in temp_vector[1]:
                            temp_vector[1][sub_parameter_key] = []

                        option_found = False
                        for temp_option in temp_vector[1][sub_parameter_key]:
                            if temp_option[0] == sub_parameter_index:
                                temp_option[1][sub_parameter_sub_key] = value
                                option_found = True
                                break

                        if not option_found:
                            temp_vector[1][sub_parameter_key].append((sub_parameter_index, {
                                sub_parameter_sub_key: value
                            }))
                    else:
                        temp_vector[1][vector_parameter_key] = value

                    found = True
                    break

            if not found:
                split_sub_key_strings = vector_parameter_key.split('_')
                if len(split_sub_key_strings) > 1:
                    sub_parameter_key = split_sub_key_strings[0]
                    sub_parameter_index = int(split_sub_key_strings[1])
                    sub_parameter_sub_key = split_sub_key_strings[2]

                    sub_parameter_key += "s"

                    temp_vectors.append((vector_index, {sub_parameter_key: [
                        (sub_parameter_index, {
                            sub_parameter_sub_key: value
                        })
                    ]}))
                else:
                    temp_vectors.append((vector_index, {vector_parameter_key: value}))

    final_parsed_vectors = [temp_vector[1] for temp_vector in sorted(temp_vectors, key=lambda temp: temp[0])]

    for parsed_vector in final_parsed_vectors:
        for key, value in parsed_vector.iteritems():
            if key == "clearInfections" or key == "deploys":
                new_value = [v[1] for v in sorted(value, key=lambda val: val[0])]
                parsed_vector[key] = new_value

    return final_parsed_vectors


def parse_larviciding_interventions(scenario):
    interventions = []

    for vector_pop in scenario.interventions.vectorPop:
        times = [str(t) for t in vector_pop.timesteps]
        component_info = {'timesteps': ','.join(times) if len(times) > 0 else "0", 'deploy': len(times) > 0,
                          'name': vector_pop.name}

        vectors = []
        for anopheles in vector_pop.anopheles:
            vector_info = {
                'mosquito': anopheles.mosquito,
                'seekingDeathRateIncrease': anopheles.seekingDeathRateIncrease,
                'probDeathOvipositing': anopheles.probDeathOvipositing,
                'emergenceReduction': anopheles.emergenceReduction
            }
            vectors.append(vector_info)

        component_info["vectors"] = vectors
        component_info["emergence_reduction"] = vectors[0]['emergenceReduction']
        interventions.append(component_info)

    return interventions


def parse_initial_options(interventions):
    mda_options = []
    for intervention in interventions:
        mda_options.append(intervention['options'])

    return mda_options


def parse_mda_interventions(scenario):
    interventions = []

    for component in scenario.interventions.human:
        if type(component) == MDA:
            component_info = {'id': component.id, 'name': component.name, "options": component.treatment_options}
            interventions.append(component_info)

    return interventions


def parse_vaccine_interventions(scenario):
    interventions = []

    for component in scenario.interventions.human:
        if type(component) == Vaccine:
            component_info = {'attrition': component.decay.L, 'efficacy_b': component.efficacyB,
                              'id': component.id, 'name': component.name}
            initial_efficacy_values = [str(value) for value in component.initialEfficacy]
            component_info["initial_efficacy"] = ','.join(initial_efficacy_values)

            interventions.append(component_info)

    return interventions


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


def load_interventions_data(scenario):
    gvi_interventions = parse_gvi_interventions(scenario)
    larviciding_interventions = parse_larviciding_interventions(scenario)
    mda_interventions = parse_mda_interventions(scenario)
    vaccine_interventions = parse_vaccine_interventions(scenario)
    imported_infections = parse_imported_infections(scenario)

    gvi_vectors = parse_initial_vectors(gvi_interventions)
    larviciding_vectors = parse_initial_vectors(larviciding_interventions)
    mda_options = parse_initial_options(mda_interventions)

    gvi = InterventionSnippet.objects.get(name="GVI")
    gvi_component = GVI(ElementTree.fromstring(gvi.xml))
    vector_pop = InterventionSnippet.objects.get(name="Larviciding")
    vector_pop_intervention = VectorPopIntervention(ElementTree.fromstring(vector_pop.xml))

    ScenarioGviInterventionFormSet = formset_factory(wraps(ScenarioGviInterventionForm)
                                                     (partial(ScenarioGviInterventionForm, component=gvi_component,
                                                              vectors_iterator=iter(gvi_vectors))), extra=0,
                                                     can_delete=True)
    ScenarioLarvicidingInterventionFormSet = formset_factory(wraps(ScenarioLarvicidingInterventionForm)
                                                             (partial(ScenarioLarvicidingInterventionForm,
                                                                      intervention=vector_pop_intervention,
                                                                      vectors_iterator=iter(larviciding_vectors))),
                                                             extra=0,
                                                             can_delete=True)
    ScenarioMdaInterventionFormSet = formset_factory(wraps(ScenarioMdaInterventionForm)
                                                     (partial(ScenarioMdaInterventionForm,
                                                              options_iterator=iter(mda_options))), extra=0,
                                                     can_delete=True)
    ScenarioVaccineInterventionFormSet = formset_factory(ScenarioVaccineInterventionForm, extra=0, can_delete=True)
    ScenarioImportedInfectionsFormSet = formset_factory(ScenarioImportedInfectionsForm, extra=0, can_delete=True)

    formsets = [
        ScenarioGviInterventionFormSet(initial=gvi_interventions, prefix='gvi'),
        ScenarioLarvicidingInterventionFormSet(initial=larviciding_interventions, prefix='intervention'),
        ScenarioMdaInterventionFormSet(initial=mda_interventions, prefix='mda'),
        ScenarioVaccineInterventionFormSet(initial=vaccine_interventions, prefix='vaccine'),
        ScenarioImportedInfectionsFormSet(initial=imported_infections, prefix='importedinfections')
    ]

    context = {}
    context["intervention_formsets"] = formsets
    context["interventions"] = InterventionSnippet.objects.all()
    context["entomology_vectors_count"] = len(scenario.entomology.vectors)
    context["entomology_vectors_names"] = [vector.mosquito for vector in scenario.entomology.vectors]

    return context


def update_interventions_form(request, scenario_id):
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

    extra_data = load_interventions_data(temp_scenario)

    html = render_to_string("ts_om_edit/interventions/interventions_list.html", extra_data)

    return HttpResponse(html)
