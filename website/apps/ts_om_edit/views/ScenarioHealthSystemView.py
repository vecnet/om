import json
from django.http import HttpResponse
from vecnet.openmalaria.healthsystem import get_percentage_from_prob, get_prob_from_percentage

from website.apps.ts_om_edit.forms import ScenarioHealthSystemForm
from website.apps.ts_om.views.ScenarioBaseFormView import ScenarioBaseFormView
from website.apps.ts_om.views.ScenarioBaseFormView import update_form


INITIAL_DRUG_VALUE = 0.96
DRUG_NAME = "clear blood-stage infections"
TREATMENT_ACTION_STAGE = "blood"
TREATMENT_ACTION_TIMESTEPS = 1


class ScenarioHealthSystemView(ScenarioBaseFormView):
    template_name = "ts_om_edit/healthsystem.html"
    form_class = ScenarioHealthSystemForm
    next_url = 'ts_om.entomology'
    step = "health system"

    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    # def get_success_url(self):
    #     return reverse('ts_om.entomology', kwargs={'scenario_id': self.kwargs['scenario_id']})

    def get_context_data(self, **kwargs):
        context = super(ScenarioHealthSystemView, self).get_context_data(**kwargs)

        context['initial_drug_value'] = INITIAL_DRUG_VALUE
        context['drug_name'] = DRUG_NAME

        return context

    def get_initial(self):
        initial = {"first_line_drug": self.scenario.healthSystem.ImmediateOutcomes.firstLine}

        seek_uncomp = self.scenario.healthSystem.ImmediateOutcomes.pSeekOfficialCareUncomplicated1
        self_treat = self.scenario.healthSystem.ImmediateOutcomes.pSelfTreatUncomplicated

        perc_total = get_percentage_from_prob(seek_uncomp)
        perc_formal = 100 - get_percentage_from_prob(self_treat)

        initial["perc_total_treated"] = perc_total
        initial["perc_formal_care"] = perc_formal

        return initial

    def form_invalid(self, form):
        response = super(ScenarioHealthSystemView, self).form_invalid(form)

        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response

    def form_valid(self, form, **kwargs):
        prob_total = get_prob_from_percentage(int(form.cleaned_data["perc_total_treated"]))
        perc_formal = int(form.cleaned_data["perc_formal_care"])
        prob_formal = get_prob_from_percentage(100-perc_formal)

        # total % (uncomplicated) fevers treated converted to probability.
        self.scenario.healthSystem.ImmediateOutcomes.pSeekOfficialCareUncomplicated1 = prob_total
        self.scenario.healthSystem.ImmediateOutcomes.pSeekOfficialCareUncomplicated2 = prob_total

        # % treated in a health clinic (formal care).
        self.scenario.healthSystem.ImmediateOutcomes.pSelfTreatUncomplicated = prob_formal

        first_line_drug = form.cleaned_data["first_line_drug"]

        self.scenario.healthSystem.ImmediateOutcomes.firstLine = first_line_drug
        self.scenario.healthSystem.ImmediateOutcomes.drugs.add(first_line_drug, unicode(INITIAL_DRUG_VALUE),
                                                               ["initialACR", "compliance", "nonCompliersEffective"])

        drug = self.scenario.healthSystem.ImmediateOutcomes.drugs[first_line_drug]
        drug.treatmentAction = DRUG_NAME
        drug.treatmentAction.stage = TREATMENT_ACTION_STAGE
        drug.treatmentAction.timesteps = TREATMENT_ACTION_TIMESTEPS

        return super(ScenarioHealthSystemView, self).form_valid(form, kwargs={'xml': self.scenario.xml})

def update_healthsystem_form(request, scenario_id):
    data = update_form(request, scenario_id)
    temp_scenario = None

    if "valid" not in data:
        return data

    valid = data["valid"]

    if not valid:
        return data

    if "scenario" in data:
        temp_scenario = data["scenario"]

    form_values = {'valid': data["valid"]}

    seek_uncomp = temp_scenario.healthSystem.ImmediateOutcomes.pSeekOfficialCareUncomplicated1
    self_treat = temp_scenario.healthSystem.ImmediateOutcomes.pSelfTreatUncomplicated

    perc_total = get_percentage_from_prob(seek_uncomp)
    perc_formal = 100 - get_percentage_from_prob(self_treat)

    form_values["perc_total_treated"] = perc_total
    form_values["perc_formal_care"] = perc_formal
    form_values["first_line_drug"] = temp_scenario.healthSystem.ImmediateOutcomes.firstLine

    return HttpResponse(json.dumps(form_values), content_type="application/json")
