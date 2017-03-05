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

import StringIO
from django.core.files.base import ContentFile, File
from django.test.testcases import TestCase

from website.apps.ts_om.models import Simulation


class Test(TestCase):
    def test(self):
        simulation = Simulation.objects.create()
        f = ContentFile("123456")
        fp = File(open("LICENSE.txt"))
        simulation.input_file.save("1234.txt", fp)

        # print simulation
        # print simulation.input_file.name
        #
        # sim = Simulation.objects.get(pk=simulation.pk)
        # print sim
        # print sim.input_file.name

