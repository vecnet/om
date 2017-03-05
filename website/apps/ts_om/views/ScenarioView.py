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
import zipfile
from StringIO import StringIO

from django.conf import settings
from django.http import HttpResponse
from lxml import etree

from website.apps.ts_om.models import Scenario, ExperimentFile
from website.apps.ts_om.views.ScenarioValidationView import rest_validate


def download_scenario_xml_view(request, scenario_id):
    if not request.user.is_authenticated() or not scenario_id or scenario_id < 0:
        return

    scenario = Scenario.objects.get(user=request.user, id=int(scenario_id))

    if not scenario:
        return

    f = StringIO(str(scenario.xml))
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(f, parser)
    xml = etree.tostring(tree.getroot(), encoding='UTF-8', pretty_print=True)

    return HttpResponse(xml)


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


def save_scenario(request, scenario_id):
    if not request.user.is_authenticated() or not scenario_id or scenario_id < 0:
        return

    xml_file = request.read()
    json_str = rest_validate(xml_file)
    validation_result = json.loads(json_str)

    valid = True if (validation_result['result'] == 0) else False

    if not valid:
        return HttpResponse(json_str, content_type="application/json")

    scenario = Scenario.objects.get(user=request.user, id=int(scenario_id))

    if not scenario:
        return HttpResponse({'saved': False}, content_type="application/json")

    scenario.xml = xml_file
    scenario.save()

    return HttpResponse(json.dumps({'saved': True}), content_type="application/json")


