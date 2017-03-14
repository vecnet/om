# Copyright (C) 2016, University of Notre Dame
# All rights reserved
import zipfile

from django.conf import settings
from django.http import HttpResponse

from website.apps.ts_om.models import ExperimentFile


def download_experiment_scenario(request, scenario_id, index):
    scenario_id = int(scenario_id)
    index = int(index)
    xml = ""

    if not request.user.is_authenticated() or not scenario_id or scenario_id < 0:
        return

    experiment = ExperimentFile.objects.get(user=request.user, id=int(scenario_id))

    if not experiment:
        return

    experiment_file = experiment.file
    proj_path = getattr(settings, "MEDIA_ROOT", None)
    full_path = proj_path + "/" + experiment_file.url

    if zipfile.is_zipfile(experiment_file):
        exp_zip = zipfile.ZipFile(full_path)
        name_lst = exp_zip.namelist()

        n = [name for name in name_lst if name.endswith(".xml")][index]
        with exp_zip.open(n) as exp_file:
            xml = exp_file.read()
    else:
        if experiment_file.url.endswith(".xml"):
            xml = experiment_file.read()

    return HttpResponse(xml, content_type="text/xml")