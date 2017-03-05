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

from django.contrib.auth.models import User

from vecnet.simulation import sim_model, sim_status
from vecnet.openmalaria import get_schema_version_from_xml

from data_services.models import SimulationGroup, Simulation as OldSimulation, SimulationInputFile

from sim_services_local import dispatcher
from website.apps.ts_om.models import Simulation


def submit_new(scenario):
    simulation = Simulation.objects.create()
    simulation.set_input_file(scenario.xml)
    try:
        dispatcher.submit_new(simulation)
        scenario.new_simulation = simulation
        scenario.save(update_fields=["new_simulation"])
        return simulation
    except RuntimeError:
        return None


def submit(user, xml, version=None):
    # Create Simulation and SimulationGroup
    if isinstance(user, (str, unicode)):
        user = User.objects.get(username=user)

    sim_group = SimulationGroup(submitted_by_user=user)
    sim_group.save()

    simulation = add_simulation(sim_group, xml, version=version)
    try:
        dispatcher.submit(sim_group)
        return simulation
    except RuntimeError:
        return None


def submit_group(user, xml_scenarios, version=None):
    # Create Simulation and SimulationGroup
    if isinstance(user, (str, unicode)):
        user = User.objects.get(username=user)

    sim_group = SimulationGroup(submitted_by_user=user)
    sim_group.save()
    for scenario in xml_scenarios:
        add_simulation(sim_group, scenario, version=version)
    try:
        dispatcher.submit(sim_group)
        return sim_group
    except RuntimeError:
        return None


def add_simulation(sim_group, xml, version=None, input_file_metadata=None):
    """
    Adds a new simulation for a scenario to a simulation group.

    :param sim_group: The group to add the simulation to.
    :param str xml: The scenario's parameters in XML format.
    :return Simulation: The new simulation.
    """
    assert isinstance(sim_group, SimulationGroup)
    if version is None:
        # Extract schemaVersion from the xml
        version = get_schema_version_from_xml(xml)
    assert version == "32" or version == "30" or version == "33"

    scenario_file = SimulationInputFile.objects.create_file(contents=xml,
                                                            name="scenario.xml",
                                                            metadata="{}")
    if input_file_metadata is not None:
        for item in input_file_metadata:
            # Note that scenario_file.metadata is dict after calling create_file
            scenario_file.metadata[item] = input_file_metadata[item]  # "scenario32.xml"
    scenario_file.save()

    simulation = OldSimulation(group=sim_group,
                            model=sim_model.OPEN_MALARIA,
                            version=version,
                            status=sim_status.READY_TO_RUN)
    simulation.save()
    simulation.input_files.add(scenario_file)
    return simulation
