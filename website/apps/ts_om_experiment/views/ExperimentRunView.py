import json

from django.http import HttpResponse
from django.views.generic import TemplateView

from data_services.models import Simulation
from website.apps.ts_om.models import ExperimentFile

__author__ = 'nreed'


class ExperimentRunView(TemplateView):
    template_name = "ts_om_experiment/run.html"

    def get_context_data(self, **kwargs):
        context = super(ExperimentRunView, self).get_context_data(**kwargs)

        if "experiment_id" in self.kwargs:
            experiment_id = self.kwargs["experiment_id"]
            run_type = self.kwargs["run_type"]
            experiment = ExperimentFile.objects.get(id=experiment_id)
            group = experiment.sim_group if run_type == 'run' else experiment.test_sim_group

            context["experiment_id"] = experiment_id
            context["name"] = experiment.name
            context["sims"] = get_run_status_for_experiment(experiment, run_type)["sims"]
            context["group_id"] = group.id

        return context


def get_sim_group_status(request, experiment_id, run_type):
    if request.is_ajax():
        data = get_run_status(experiment_id, run_type)

        return HttpResponse(json.dumps(data), mimetype="application/json")


def get_run_status(experiment_id, run_type='run'):
    experiment = ExperimentFile.objects.get(id=experiment_id)

    return get_run_status_for_experiment(experiment, run_type)


def get_run_status_for_experiment(experiment, run_type):
    data = {'sims': []}
    group = experiment.sim_group if run_type == 'run' else experiment.test_sim_group

    for sim in Simulation.objects.filter(group=group):
        sim = {'id': str(sim.id), 'status': str(sim.status)}
        data['sims'].append(sim)

    return data


def download_experiment_zip(request, experiment_id, run_type):
    experiment = ExperimentFile.objects.get(id=experiment_id)

    sim_group = experiment.test_sim_group if run_type == "test" else experiment.sim_group

    zip_contents, zip_len = sim_group.create_om_zip_file("experiment")

    resp = HttpResponse(zip_contents, content_type="application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment; filename=%s' % 'experiment.zip'
    resp['Content-Length'] = zip_len

    return resp
