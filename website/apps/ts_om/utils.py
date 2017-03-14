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
from xml.etree.ElementTree import ParseError

from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.http import HttpResponse
from vecnet.openmalaria.scenario import Scenario

from data_services.models import Simulation
from website.apps.ts_om.models import Simulation as SimulationNew, Scenario as ScenarioModel
from website.apps.ts_om.views.ScenarioValidationView import rest_validate


def migrate_simulations():
    # This function is for use in data migration. Should be removed after data on the server has been migrated
    for simulation in Simulation.objects.all():
        print simulation.id
        simulation_new = SimulationNew()
        input_file = simulation.input_files.filter(name="scenario.xml").first()
        if input_file:
            print input_file
            simulation_new.input_file.save(
                "scenario_%s.xml" % simulation_new.id,
                ContentFile(input_file.get_contents())
            )
        output_file = simulation.simulationoutputfile_set.filter(name="output.txt").first()
        if output_file:
            print output_file
            simulation_new.output_file.save(
                "output_%s.txt" % simulation_new.id,
                ContentFile(output_file.get_contents())
            )

        ctsout_file = simulation.simulationoutputfile_set.filter(name="ctsout.txt").first()
        if ctsout_file:
            print ctsout_file
            simulation_new.ctsout_file.save(
                "ctsout_%s.txt" % simulation_new.id,
                ContentFile(ctsout_file.get_contents())
            )

        stdout = simulation.simulationoutputfile_set.filter(name="stdout.txt").first()
        if stdout:
            print stdout
            simulation_new.model_stdout.save(
                "stdout_%s.txt" % simulation_new.id,
                ContentFile(stdout.get_contents())
            )

        if simulation.status == "done":
            simulation_new.status = SimulationNew.COMPLETE
        elif simulation.status == "error":
            simulation_new.status = SimulationNew.FAILED
        elif simulation.status == "ready":
            simulation_new.status = SimulationNew.NEW

        simulation_new.save()
        scenario = simulation.scenario_set.all().first()
        if scenario:
            scenario.new_simulation = simulation_new
            scenario.save()


def update_form(request, scenario_id):
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

    return {"valid": valid, "scenario": temp_scenario}