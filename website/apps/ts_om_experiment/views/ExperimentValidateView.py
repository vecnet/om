# PEP 0263
# -*- coding: utf-8 -*-
########################################################################################################################
# VECNet CI - Prototype
# Date: 4/5/2013
# Institution: University of Notre Dame
# Primary Authors:
#   Nicolas Reed <Nicolas.Reed.102@nd.edu>
########################################################################################################################

import json
import zipfile
from django.core.paginator import Paginator
import os

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.views.generic import ListView

from website.apps.ts_om import submit
from website.apps.ts_om.models import ExperimentFile
from website.apps.ts_om.models import Scenario
from website.apps.ts_om.views.ScenarioValidationView import rest_validate

__author__ = 'nreed'


class ExperimentValidateView(ListView):
    template_name = "ts_om_experiment/validate.html"
    model = Scenario
    paginate_by = 10
    experiment = None
    scenarios = None

    def post(self, request):
        experiment_id = self.request.session['experiment_id']
        experiment = ExperimentFile.objects.get(id=experiment_id)

        scenarios = get_scenarios(experiment.file, False, 100)
        submit_group = submit.submit_group(self.request.user, scenarios)

        submit_type = "run"
        if submit_group:
            if len(scenarios) > 100:
                experiment.test_sim_group = submit_group
                submit_type = "test"
            else:
                experiment.sim_group = submit_group
            experiment.save()
        else:
            return HttpResponseRedirect(reverse("ts_om.validate"))

        return HttpResponseRedirect(reverse('ts_om.run', kwargs={'experiment_id': experiment_id, 'run_type': submit_type}))

    def get_context_data(self, **kwargs):
        experiment_id = self.request.session['experiment_id']
        experiment = ExperimentFile.objects.get(id=experiment_id)

        validation_info = get_scenarios(experiment.file, True)[1]

        kwargs['object_list'] = validation_info

        context = super(ExperimentValidateView, self).get_context_data(**kwargs)
        name = self.request.session['name']

        rc = [item[1] for item in validation_info]
        failure_count = len([c for c in rc if c == "FAILED"])
        failure = len(rc) == 0 or failure_count > 0

        context['name'] = name
        context['status'] = failure

        if failure:
            context['failure_count'] = failure_count

        context['scenarios'] = validation_info
        context['experiment_id'] = experiment.id
        context['experiment_file_url'] = experiment.file.url

        paginator = Paginator(validation_info, self.paginate_by)
        context['page_range'] = range(paginator.num_pages)

        return context


def get_scenarios(experiment_file, validate=False, count=-1):
    scenarios = []
    names = []
    rc = []
    data = []

    proj_path = getattr(settings, "MEDIA_ROOT", None)
    full_path = proj_path + "/" + experiment_file.url

    if zipfile.is_zipfile(experiment_file):
        exp_zip = zipfile.ZipFile(full_path)
        name_lst = exp_zip.namelist()

        for n in name_lst:
            if n.endswith(".xml"):
                if -1 < count <= len(scenarios):
                    break

                with exp_zip.open(n) as exp_file:
                    xml = exp_file.read()

                    if validate:
                        temp = json.loads(rest_validate(xml))

                    scenarios.append(xml)

                    if validate:
                        names.append(n)
                        rc.append("VALID" if (temp['result'] == 0) else "FAILED")
                        data.append(temp['om_output'])
    else:
        if experiment_file.url.endswith(".xml"):
            xml = experiment_file.read()
            temp = json.loads(rest_validate(xml))

            scenarios.append(xml)

            if validate:
                names.append(os.path.basename(experiment_file.url))
                rc.append("VALID" if (temp['result'] == 0) else "FAILED")
                data.append(temp['om_output'])

    if validate:
        return [scenarios, zip(names, rc, data)]

    return scenarios


def get_validation_status():
    # TODO: Implement validation.
    pass


def check_validation_status(request):
    if request.is_ajax():
        data = get_validation_status()

        return HttpResponse(json.dumps(data), mimetype="application/json")
