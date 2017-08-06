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

from django.test import TestCase

from website.apps.ts_om.models import Simulation
from website.apps.ts_om.utils import get_simulations_in_progress


class GetSimulationsInProgressTest(TestCase):
    def setUp(self):
        pass

    def test_1(self):
        simulation = Simulation.objects.create()
        self.assertEqual(list(get_simulations_in_progress()), [])

    def test_2(self):
        simulation = Simulation.objects.create(status=Simulation.RUNNING)
        self.assertEqual(list(get_simulations_in_progress()), [simulation])
