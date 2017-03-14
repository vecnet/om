from functools import partial, wraps
import json
from xml.etree.ElementTree import ParseError

from django.core.exceptions import PermissionDenied
from django.forms.formsets import formset_factory
from django.http import HttpResponse
from django.template.loader import render_to_string
from vecnet.openmalaria.scenario import Scenario

from website.apps.ts_om.models import Scenario as ScenarioModel
from website.apps.ts_om_edit.forms import ScenarioDeploymentsForm, ScenarioDeploymentForm
from website.apps.ts_om_edit.views.ScenarioBaseFormView import ScenarioBaseFormView
from website.apps.ts_om.views.ScenarioValidationView import rest_validate

__author__ = 'nreed'


class ScenarioDeploymentsView(ScenarioBaseFormView):
    template_name = "ts_om_edit/deployments.html"
    form_class = ScenarioDeploymentsForm
    next_url = 'ts_om.summary2'
    step = "deployments"


    def get_context_data(self, **kwargs):
        context = super(ScenarioDeploymentsView, self).get_context_data(**kwargs)

        extra_data = load_deployments_data(self.scenario)

        new_context = context.copy()
        new_context.update(extra_data)

        return new_context

    def form_valid(self, form, **kwargs):
        component_ids = []
        for intervention in self.scenario.interventions.human:
            component_ids.append((intervention.id, intervention.id))

        ScenarioDeploymentFormSet = formset_factory(wraps(ScenarioDeploymentForm)
                                                    (partial(ScenarioDeploymentForm, components=component_ids)),
                                                    extra=0, can_delete=True)
        deployment_formset = ScenarioDeploymentFormSet(self.request.POST, prefix='deployment')

        if not deployment_formset.is_valid():
            return super(ScenarioDeploymentsView, self).form_invalid(form)

        deployments = []
        for form in deployment_formset:
            deployment_info = {
                'components': form.cleaned_data["components"]
            }

            if 'xml' in form.cleaned_data and form.cleaned_data["xml"]:
                # Preserve "continuous" deployment as a workaround for internal server error
                deployment_info["xml"] = form.cleaned_data["xml"]
            else:
                if 'name' in form.cleaned_data and form.cleaned_data["name"] != "":
                    deployment_info['name'] = form.cleaned_data["name"]

                times = form.cleaned_data["timesteps"].split(',')
                coverages = form.cleaned_data["coverages"].split(',')
                timesteps = []
                for index, time in enumerate(times):
                    timesteps.append({
                        "time": time,
                        "coverage": coverages[index] if len(coverages) > index else coverages[0]
                    })

                deployment_info["timesteps"] = timesteps
            deployments.append(deployment_info)

        self.scenario.interventions.human.deployments = deployments

        return super(ScenarioDeploymentsView, self).form_valid(form, kwargs={'xml': self.scenario.xml})


def parse_deployments(scenario):
    deployments = []

    for deployment in scenario.interventions.human.deployments:
        deployment_info = {'components': deployment.components}

        try:
            deployment_info["name"] = deployment.name
        except AttributeError:
            pass

        deployment_info["xml"] = ""
        try:
            timesteps = deployment.timesteps
        except:
            # Temp workaround for internal server error when using <continuous> deployment
            deployment_info["xml"] = deployment.xml
            deployment_info["timesteps"] = '1'
            deployment_info["coverages"] = '1'
            deployments.append(deployment_info)
            continue

        times = [str(timestep["time"]) for timestep in timesteps]
        coverages = [str(timestep["coverage"]) for timestep in timesteps]

        deployment_info["timesteps"] = ','.join(times)
        deployment_info["coverages"] = ','.join(coverages)

        deployments.append(deployment_info)

    return deployments


def load_deployments_data(scenario):
    component_ids = []
    for intervention in scenario.interventions.human:
        component_ids.append((intervention.id, intervention.id))

    ScenarioDeploymentFormSet = formset_factory(wraps(ScenarioDeploymentForm)
                                                (partial(ScenarioDeploymentForm, components=component_ids)),
                                                extra=0, can_delete=True)
    deployment_formset = ScenarioDeploymentFormSet(initial=parse_deployments(scenario),
                                                   prefix='deployment')

    context = {}
    context["deployment_formset"] = deployment_formset
    context["has_components"] = len(component_ids) > 0

    return context


def update_deployments_form(request, scenario_id):
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

    extra_data = load_deployments_data(temp_scenario)

    html = render_to_string("ts_om_edit/deployments_list.html", extra_data)

    return HttpResponse(html)
