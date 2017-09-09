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
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError
from functools import partial, wraps

from django.core.exceptions import PermissionDenied
from django.forms.formsets import formset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.db.models import Q
from vecnet.openmalaria.scenario import Scenario
from vecnet.openmalaria.scenario.interventions import GVI, MDA, Vaccine, VectorPopIntervention

from website.apps.ts_om_edit.forms import ScenarioInterventionsForm, ScenarioGviInterventionForm, \
    ScenarioLarvicidingInterventionForm, ScenarioMdaInterventionForm, ScenarioVaccineInterventionForm
from website.apps.ts_om.models import Scenario as ScenarioModel, InterventionSnippet
from website.apps.ts_om_edit.views.ScenarioBaseFormView import ScenarioBaseFormView
from website.apps.ts_om.views.ScenarioValidationView import rest_validate
import logging
logger = logging.getLogger(__name__)


class ScenarioInterventionsView(ScenarioBaseFormView):
    template_name = "ts_om_edit/interventions.html"
    form_class = ScenarioInterventionsForm
    next_url = 'ts_om.deployments'
    prev_url = 'ts_om.entomology'
    step = "interventions"

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
        larviciding_vectors = parse_parameters(self.request.POST, "larviciding")
        mda_options = parse_options(self.request.POST, "mda")

        ScenarioGviInterventionFormSet = formset_factory(wraps(ScenarioGviInterventionForm)
                                                         (partial(ScenarioGviInterventionForm, vectors=gvi_vectors)),
                                                         extra=0, can_delete=True)
        ScenarioLlinInterventionFormSet = formset_factory(wraps(ScenarioGviInterventionForm)
                                                 (partial(ScenarioGviInterventionForm)),
                                                 extra=0, can_delete=True)
        ScenarioIrsInterventionFormSet = formset_factory(wraps(ScenarioGviInterventionForm)
                                                          (partial(ScenarioGviInterventionForm)),
                                                          extra=0, can_delete=True)
        ScenarioPyrethroidsInterventionFormSet = formset_factory(wraps(ScenarioGviInterventionForm)
                                                         (partial(ScenarioGviInterventionForm)),
                                                         extra=0, can_delete=True)
        ScenarioDdtInterventionFormSet = formset_factory(wraps(ScenarioGviInterventionForm)
                                                         (partial(ScenarioGviInterventionForm)),
                                                         extra=0, can_delete=True)
        ScenarioLarvicidingInterventionFormSet = formset_factory(wraps(ScenarioLarvicidingInterventionForm)
                                                                 (partial(ScenarioLarvicidingInterventionForm,
                                                                          vectors=larviciding_vectors)), extra=0,
                                                                 can_delete=True)
        ScenarioMdaInterventionFormSet = formset_factory(wraps(ScenarioMdaInterventionForm)
                                                         (partial(ScenarioMdaInterventionForm, options=mda_options)),
                                                         extra=0, can_delete=True)
        ScenarioVaccineBsvInterventionFormSet = formset_factory(ScenarioVaccineInterventionForm, extra=0,
                                                                can_delete=True)
        ScenarioVaccinePevInterventionFormSet = formset_factory(ScenarioVaccineInterventionForm, extra=0,
                                                                can_delete=True)
        ScenarioVaccineTbvInterventionFormSet = formset_factory(ScenarioVaccineInterventionForm, extra=0,
                                                                can_delete=True)

        formsets = [
            ScenarioGviInterventionFormSet(self.request.POST, prefix='gvi'),
            ScenarioLlinInterventionFormSet(self.request.POST, prefix='llin'),
            ScenarioIrsInterventionFormSet(self.request.POST, prefix='irs'),
            ScenarioPyrethroidsInterventionFormSet(self.request.POST, prefix='pyrethroids'),
            ScenarioDdtInterventionFormSet(self.request.POST, prefix='ddt'),
            ScenarioLarvicidingInterventionFormSet(self.request.POST, prefix='larviciding'),
            ScenarioMdaInterventionFormSet(self.request.POST, prefix='mda'),
            ScenarioVaccineBsvInterventionFormSet(self.request.POST, prefix='vaccine-bsv'),
            ScenarioVaccinePevInterventionFormSet(self.request.POST, prefix='vaccine-pev'),
            ScenarioVaccineTbvInterventionFormSet(self.request.POST, prefix='vaccine-tbv'),
        ]
        logger.debug(formsets)
        for formset in formsets:
            if not formset.is_valid():
                logger.debug("Formset is invalid, " % formset.errors)
                return super(ScenarioInterventionsView, self).form_invalid(form)

        logger.debug("Interventions - all formsets are valid")
        human_intervention_ids = []
        vectorpop_intervention_names = []

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

                        if component_tag.startswith("vaccine"):
                            component_tag = name
                        elif (component_tag == "llin" or component_tag == "irs" or component_tag == "pyrethroids" or
                                      component_tag == "ddt"):
                            component_tag = "gvi"

                        possible_snippets = InterventionSnippet.objects.filter(component__tag__iexact=component_tag)
                        if possible_snippets is not None:
                            snippet = possible_snippets.get(name=name)

                            if snippet is None:
                                if formset.prefix == "gvi":
                                    snippet = possible_snippets.get(name="GVI")
                                elif formset.prefix == "llin":
                                    snippet = possible_snippets.get(name="LLIN")
                                elif formset.prefix == "irs":
                                    snippet = possible_snippets.get(name="IRS")
                                elif formset.prefix == "pyrethroids":
                                    snippet = possible_snippets.get(name="Pyrethroids")
                                elif formset.prefix == "ddt":
                                    snippet = possible_snippets.get(name="DDT")
                                elif formset.prefix == "mda":
                                    snippet = possible_snippets.get(name="Coarthem")
                                elif formset.prefix == "vaccine-bsv":
                                    snippet = possible_snippets.get(name="BSV")
                                elif formset.prefix == "vaccine-pev":
                                    snippet = possible_snippets.get(name="PEV")
                                elif formset.prefix == "vaccine-tbv":
                                    snippet = possible_snippets.get(name="TBV")

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

                        if (formset.prefix == "gvi" or formset.prefix == "llin" or formset.prefix == "irs" or
                                    formset.prefix == "pyrethroids" or formset.prefix == "ddt" and
                                'attrition' in form.cleaned_data):
                            intervention.decay.L = float(form.cleaned_data['attrition'])
                            temp_vectors = parse_parameters(self.request.POST, formset.prefix, index=index)
                            for vector in temp_vectors:
                                intervention.add_or_update_anophelesParams(vector)
                        elif formset.prefix == "mda":
                            temp_options = parse_options(self.request.POST, formset.prefix,
                                                         index=index)
                            for option in temp_options:
                                intervention.add_or_update_treatment_option(option)
                        elif formset.prefix.startswith("vaccine"):
                            intervention.decay.L = float(form.cleaned_data["attrition"])
                            intervention.efficacyB = float(form.cleaned_data["efficacy_b"])
                            intervention.initialEfficacy = form.cleaned_data["initial_efficacy"].split(',')
                else:
                    if formset.prefix == 'larviciding':
                        vectorpop_intervention_names.append(name)

                        try:
                            intervention = self.scenario.interventions.vectorPop[name]
                        except KeyError:
                            possible_snippets = InterventionSnippet.objects.filter(
                                component__tag__iexact="intervention")
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
                              'id': component.id}

            try:
                component_info["name"] = component.name
            except AttributeError:
                pass

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


def parse_inner_data(post_data, prefix, data_type="vector", index=0, inner_func=None):
    """Parses a variable number of dynamically added form fields.

    This essentially provides parsing of nested 'formsets'.

    :param post_data: The QueryDict from the POST HttpRequest.
    :param prefix: Formset prefix to filter on.
    :param data_type: String to filter on.
    :param index: The index of the form to filter on.
    :param inner_func: Optional function that can be called to do further work.
    :return: An array of data points containing data_type-specific data.
    """
    data_points = []
    ignored_substring = "inner-prefix"

    for key, value in post_data.iteritems():
        if ignored_substring in key or prefix not in key or data_type not in key:
            continue

        split_key = key.split('-')
        try:
            form_index = int(split_key[1])
        except ValueError:
            continue

        if form_index != index:
            continue

        split_data_key = split_key[2].split('_', 2)
        data_index = split_data_key[1]
        data_parameter_key = split_data_key[2]

        found = False
        for data_point in data_points:
            if data_point["index"] == data_index:
                inner_func_args = (data_parameter_key, data_point, value)
                if inner_func is None or not inner_func(*inner_func_args):
                    data_point["data"][data_parameter_key] = value
                found = True
                break

        if not found:
            parameter_data = split_inner_data_parameter(data_parameter_key)
            if parameter_data:
                new_data_point = {
                    "index": data_index,
                    "data": {
                        parameter_data["key"]: [{
                            "index": parameter_data["index"],
                            "data": {
                                parameter_data["sub_key"]: value
                            }
                        }]
                    }
                }
                data_points.append(new_data_point)
            else:
                data_points.append({
                    "index": data_index,
                    "data": {
                        data_parameter_key: value
                    }
                })

    return [data_point["data"] for data_point in sorted(data_points, key=lambda  point: point["index"])]


def parse_parameters(post_data, prefix, index=0):
    """Obtain vector-specific data from vector-specific form fields in a POST.

    :param post_data: The QueryDict from the POST HttpRequest.
    :param prefix: Formset prefix to filter on.
    :param index: The index of the form to filter on.
    :return: An array of data points containing vector-specific data.
    """
    return parse_inner_data(post_data, prefix, data_type="vector", index=index)


def split_inner_data_parameter(data_parameter_key):
    """Split specified key string into separate sub keys and indexes.

    :param data_parameter_key: The string to split on.
    :return: A dictionary with key, index, and sub_key values.
    """
    split_data_parameter_key = data_parameter_key.split('_')
    sub_parameter_data = {}
    if len(split_data_parameter_key) > 1:
        sub_parameter_key_suffix = "s"
        sub_parameter_key = split_data_parameter_key[0] + sub_parameter_key_suffix
        try:
            sub_parameter_index = int(split_data_parameter_key[1])
        except ValueError:
            return sub_parameter_data

        sub_parameter_sub_key = split_data_parameter_key[2]

        sub_parameter_data = {
            "key": sub_parameter_key,
            "index": sub_parameter_index,
            "sub_key": sub_parameter_sub_key
        }

    return sub_parameter_data


def inner_parse_options(data_parameter_key, data_point, value):
    """Obtains nested option-specific data from mda-options.

    :param data_parameter_key: The mda-option form field's POST key.
    :param data_point: The currently parsed out data point.
    :param value: Value to be added to the data point's sub key.
    :return: Whether further parsing was successful or not.
    """
    if data_parameter_key is None or data_point is None:
        return False

    sub_parameter_data = split_inner_data_parameter(data_parameter_key)

    if not sub_parameter_data:
        return False

    sub_parameter_key = sub_parameter_data["key"]
    if sub_parameter_key not in data_point["data"]:
        data_point["data"][sub_parameter_key] = []

    sub_parameter_index = sub_parameter_data["index"]
    sub_parameter_sub_key = sub_parameter_data["sub_key"]

    found = False
    for parameter in data_point["data"][sub_parameter_key]:
        if parameter["index"] == sub_parameter_index:
            parameter["data"][sub_parameter_sub_key] = value
            found = True
            break

    if not found:
        data_parameter = {
            "index": sub_parameter_index,
            "data": {
                sub_parameter_sub_key: value
            }
        }
        data_point["data"][sub_parameter_key].append(data_parameter)

    return True


def parse_options(post_data, prefix, index=0):
    """Obtain vector-specific data from mda-option-specific form fields in a POST.

    :param post_data: The QueryDict from the POST HttpRequest.
    :param prefix: Formset prefix to filter on.
    :param index: The index of the form to filter on.
    :return: An array of data points containing mda-option-specific data.
    """
    parsed_data = parse_inner_data(post_data, prefix, data_type="option", index=index, inner_func=inner_parse_options)

    for data_point in parsed_data:
        for key, value in data_point.iteritems():
            if key == "clearInfections" or key == "deploys":
                new_value = [val["data"] for val in sorted(value, key=lambda val: val["index"])]
                data_point[key] = new_value

    return parsed_data


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
            component_info = {'id': component.id, "options": component.treatment_options}

            try:
                component_info["name"] = component.name
            except AttributeError:
                pass

            interventions.append(component_info)

    return interventions


def parse_vaccine_interventions(scenario):
    interventions = []

    for component in scenario.interventions.human:
        if type(component) == Vaccine:
            component_info = {'attrition': component.decay.L, 'efficacy_b': component.efficacyB,
                              'id': component.id, 'vaccine_type': component.vaccine_type}

            try:
                component_info["name"] = component.name
            except AttributeError:
                pass

            initial_efficacy_values = [str(value) for value in component.initialEfficacy]
            component_info["initial_efficacy"] = ','.join(initial_efficacy_values)

            interventions.append(component_info)

    return interventions


def load_interventions_data(scenario):
    gvi_interventions = parse_gvi_interventions(scenario)
    larviciding_interventions = parse_larviciding_interventions(scenario)
    mda_interventions = parse_mda_interventions(scenario)
    vaccine_interventions = parse_vaccine_interventions(scenario)

    bsv_vaccine_interventions = [vaccine_intervention for vaccine_intervention in vaccine_interventions
                                 if vaccine_intervention["vaccine_type"] == "BSV"]
    pev_vaccine_interventions = [vaccine_intervention for vaccine_intervention in vaccine_interventions
                                 if vaccine_intervention["vaccine_type"] == "PEV"]
    tbv_vaccine_interventions = [vaccine_intervention for vaccine_intervention in vaccine_interventions
                                 if vaccine_intervention["vaccine_type"] == "TBV"]

    gvi_vectors = parse_initial_vectors(gvi_interventions)
    larviciding_vectors = parse_initial_vectors(larviciding_interventions)
    mda_options = parse_initial_options(mda_interventions)

    gvi = InterventionSnippet.objects.get(name="GVI")
    gvi_component = GVI(ElementTree.fromstring(gvi.xml))

    llin = InterventionSnippet.objects.get(name="LLIN")
    llin_component = GVI(ElementTree.fromstring(llin.xml))

    irs = InterventionSnippet.objects.get(name="IRS")
    irs_component = GVI(ElementTree.fromstring(irs.xml))

    pyrethroids = InterventionSnippet.objects.get(name="Pyrethroids")
    pyrethroids_component = GVI(ElementTree.fromstring(pyrethroids.xml))

    ddt = InterventionSnippet.objects.get(name="DDT")
    ddt_component = GVI(ElementTree.fromstring(ddt.xml))

    vector_pop = InterventionSnippet.objects.get(name="Larviciding")
    vector_pop_intervention = VectorPopIntervention(ElementTree.fromstring(vector_pop.xml))

    vaccine_bsv = InterventionSnippet.objects.get(name="BSV")
    vaccine_bsv_component = Vaccine(ElementTree.fromstring(vaccine_bsv.xml))
    vaccine_pev = InterventionSnippet.objects.get(name="PEV")
    vaccine_pev_component = Vaccine(ElementTree.fromstring(vaccine_pev.xml))
    vaccine_tbv = InterventionSnippet.objects.get(name="TBV")
    vaccine_tbv_component = Vaccine(ElementTree.fromstring(vaccine_tbv.xml))

    ScenarioGviInterventionFormSet = formset_factory(wraps(ScenarioGviInterventionForm)
                                                     (partial(ScenarioGviInterventionForm, component=gvi_component,
                                                              vectors_iterator=iter(gvi_vectors))), extra=0,
                                                     can_delete=True)
    ScenarioLlinInterventionFormSet = formset_factory(wraps(ScenarioGviInterventionForm)
                                                 (partial(ScenarioGviInterventionForm, component=llin_component)),
                                                      extra=0, can_delete=True)
    ScenarioIrsInterventionFormSet = formset_factory(wraps(ScenarioGviInterventionForm)
                                             (partial(ScenarioGviInterventionForm, component=irs_component)), extra=0,
                                             can_delete=True)
    ScenarioPyrethroidsInterventionFormSet = formset_factory(wraps(ScenarioGviInterventionForm)
                                                     (partial(ScenarioGviInterventionForm,
                                                              component=pyrethroids_component)), extra=0,
                                                     can_delete=True)
    ScenarioDdtInterventionFormSet = formset_factory(wraps(ScenarioGviInterventionForm)
                                                             (partial(ScenarioGviInterventionForm,
                                                                      component=ddt_component)), extra=0,
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
    ScenarioVaccineBsvInterventionFormSet = formset_factory(wraps(ScenarioVaccineInterventionForm)
                                                         (partial(ScenarioVaccineInterventionForm,
                                                                  component=vaccine_bsv_component)), extra=0,
                                                         can_delete=True)
    ScenarioVaccinePevInterventionFormSet = formset_factory(wraps(ScenarioVaccineInterventionForm)
                                                     (partial(ScenarioVaccineInterventionForm,
                                                              component=vaccine_pev_component)), extra=0,
                                                     can_delete=True)
    ScenarioVaccineTbvInterventionFormSet = formset_factory(wraps(ScenarioVaccineInterventionForm)
                                                         (partial(ScenarioVaccineInterventionForm,
                                                                  component=vaccine_tbv_component)), extra=0,
                                                         can_delete=True)

    formsets = [
        ScenarioGviInterventionFormSet(initial=gvi_interventions, prefix='gvi'),
        ScenarioLlinInterventionFormSet(prefix='llin'),
        ScenarioIrsInterventionFormSet(prefix='irs'),
        ScenarioPyrethroidsInterventionFormSet(prefix='pyrethroids'),
        ScenarioDdtInterventionFormSet(prefix='ddt'),
        ScenarioLarvicidingInterventionFormSet(initial=larviciding_interventions, prefix='larviciding'),
        ScenarioMdaInterventionFormSet(initial=mda_interventions, prefix='mda'),
        ScenarioVaccineBsvInterventionFormSet(initial=bsv_vaccine_interventions, prefix='vaccine-bsv'),
        ScenarioVaccinePevInterventionFormSet(initial=pev_vaccine_interventions, prefix='vaccine-pev'),
        ScenarioVaccineTbvInterventionFormSet(initial=tbv_vaccine_interventions, prefix='vaccine-tbv'),
    ]

    context = {}
    context["intervention_formsets"] = formsets
    context["interventions"] = InterventionSnippet.objects.exclude(
        Q(component__tag__iexact="importedinfections") | Q(component__tag__iexact="mda") | Q(name__iexact="irs"))
    context["entomology_vectors_count"] = len(scenario.entomology.vectors)
    context["entomology_vectors_names"] = [vector.mosquito for vector in scenario.entomology.vectors]

    return context


def update_interventions_form(request, scenario_id):
    if not request.user.is_authenticated():
        raise PermissionDenied

    xml_file = request.POST['xml']
    json_str = rest_validate(xml_file)
    validation_result = json.loads(json_str)

    valid = True if (validation_result['result'] == 0) else False

    if not valid:
        return HttpResponse(json_str, content_type="application/json")

    model_scenario = get_object_or_404(ScenarioModel, id=scenario_id)

    if request.user != model_scenario.user:
        raise PermissionDenied

    temp_scenario = Scenario(xml_file)

    extra_data = load_interventions_data(temp_scenario)

    html = render_to_string("ts_om_edit/interventions/interventions_list.html", extra_data)

    return HttpResponse(html)
