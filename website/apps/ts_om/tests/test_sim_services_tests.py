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
from django.test import TestCase
from django.test.utils import override_settings
from vecnet.simulation import (sim_model, Simulation as SimulationRepresentation,
                               SimulationGroup as SimGroupRepresentation)

from .data import EMPTY_SCENARIO
from sim_services.dispatcher import create_group_resource_repr, create_sim_resource_repr, RestApi
from data_services import models as data_models


class ResourceRepresentationTests(TestCase):
    """
    Tests for the methods that generate representations of REST resources.
    """

    @classmethod
    def setUpClass(cls):
        super(ResourceRepresentationTests, cls).setUpClass()
        cls.test_user = User.objects.create(username='test-user')
        cls.sim_group = data_models.SimulationGroup.objects.create(submitted_by_user=cls.test_user)
        cls.simulation = data_models.Simulation.objects.create(group=cls.sim_group,
                                                               model=sim_model.OPEN_MALARIA,
                                                               version="32")
        cls.scenario_file = data_models.SimulationInputFile.objects.create_file(EMPTY_SCENARIO,
                                                                                name='scenario.xml')
        cls.simulation.input_files.add(cls.scenario_file)

    @override_settings(SITE_ROOT_URL="http://localhost")
    def test_simulation_representation(self):
        """
        Test the creation of a representation for a simulation resource.
        """
        sim_resource_repr = create_sim_resource_repr(self.simulation)
        self.check_simulation_representation(sim_resource_repr, self.simulation)

    def check_simulation_representation(self, sim_resource_repr, simulation):
        """
        Check the representation of a simulation against the simulation itself.
        """
        self.assertIsInstance(sim_resource_repr, SimulationRepresentation)
        self.assertEqual(sim_resource_repr.model, simulation.model)
        self.assertEqual(sim_resource_repr.model_version, simulation.version)
        self.assertEqual(sim_resource_repr.id_on_client, str(simulation.id))
        self.assertEqual(sim_resource_repr.output_url, RestApi.output_files_endpoint)
        expected_input_files = {
            'scenario.xml': RestApi.get_download_url(self.scenario_file)
        }
        self.assertEqual(sim_resource_repr.input_files, expected_input_files)

    @override_settings(SITE_ROOT_URL="http://localhost")
    def test_group_representation(self):
        """
        Test the creation of a representation for a simulation group resource.
        """
        group_resource_repr = create_group_resource_repr(self.sim_group)
        self.assertIsInstance(group_resource_repr, SimGroupRepresentation)
        self.assertEqual(group_resource_repr.default_model, None)
        self.assertEqual(group_resource_repr.default_version, None)
        self.assertEqual(len(group_resource_repr.simulations), 1)
        self.check_simulation_representation(group_resource_repr.simulations[0], self.simulation)
