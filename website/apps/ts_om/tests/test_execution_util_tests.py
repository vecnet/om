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

import mock
import sys

from django.contrib.auth.models import User
from django.test import TestCase
from vecnet.simulation import sim_model

from .data import EMPTY_SCENARIO
from website.apps.ts_om_experiment.submit import add_simulation
from data_services.models import Simulation, SimulationGroup


class AddSimulationTests(TestCase):
    """
    Tests for the add_simulation function in the execution_util module.
    """

    @classmethod
    def setUpClass(cls):
        super(AddSimulationTests, cls).setUpClass()
        cls.test_user = User.objects.create(username='test-user')
        cls.sim_group = SimulationGroup.objects.create(submitted_by_user=cls.test_user)

        # Setup mock for sys.stdout so "print" statements don't print anything
        cls.sys_stdout = sys.stdout
        sys.stdout = mock.Mock()

    @classmethod
    def tearDownClass(cls):
        sys.stdout = cls.sys_stdout
        cls.sys_stdout = None
        super(AddSimulationTests, cls).tearDownClass()

    def setUp(self):
        Simulation.objects.all().delete()

    def test_wrong_type_for_group(self):
        """
        Test the addition_simulation function when the wrong data type is passed for the simulation group.
        """
        self.assertRaises(AssertionError, add_simulation, None, "")
        self.assertRaises(AssertionError, add_simulation, list(), "")
        self.assertRaises(AssertionError, add_simulation, self, "")

    def check_simulation(self, simulation, expected_contents):
        """
        Check that the simulation belongs to the test simulation group, and has 1 input file named "scenario.xml" with
        the expected file contents.
        """
        self.assertIsInstance(simulation, Simulation)
        self.assertIs(simulation.group, self.sim_group)
        self.assertEqual(simulation.model, sim_model.OPEN_MALARIA)

        self.assertEqual(simulation.input_files.count(), 1)
        input_file = simulation.input_files.all()[0]
        self.assertEqual(input_file.name, 'scenario.xml')
        self.assertEqual(input_file.get_contents(), expected_contents)

    def test_with_empty_xml(self):
        """
        Test the addition_simulation function when the XML contents is an empty string.
        """
        simulation = add_simulation(self.sim_group, "", version="30")
        self.check_simulation(simulation, "")

    def test_with_3_simulations(self):
        """
        Test the addition_simulation function by adding 3 simulations to a group.
        """
        xml_contents = [
            "<?xml version='1.0'>",  # Just XML header
            "",                      # Empty file,
            EMPTY_SCENARIO,
        ]
        expected_count = 0
        for xml in xml_contents:
            simulation = add_simulation(self.sim_group, xml, version="30")
            self.check_simulation(simulation, xml)
            expected_count += 1
            self.assertEqual(self.sim_group.simulations.count(), expected_count)
