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
from django.test.testcases import TestCase

from website.apps.ts_om.models import AnophelesSnippet


SNIPPET = """
<anopheles mosquito="funestus" propInfected="0.078" propInfectious="0.015">
        <seasonality annualEIR="0.37" input="EIR">
          <monthlyValues smoothing="fourier">
            <value>0.68087154500000</value>
            <value>0.88260403269200</value>
            <value>1.01475682885000</value>
            <value>1.14115038462000</value>
            <value>1.08244246560000</value>
            <value>1.00177528560000</value>
            <value>0.84910486440000</value>
            <value>0.70008667400000</value>
            <value>0.63749115320000</value>
            <value>0.55536272920000</value>
            <value>0.51581716920000</value>
            <value>0.56576189328000</value>
          </monthlyValues>
        </seasonality>
        <mosq minInfectedThreshold="0.001">
          <mosqRestDuration value="2"/>
          <extrinsicIncubationPeriod value="12"/>
          <mosqLaidEggsSameDayProportion value="0.313"/>
          <mosqSeekingDuration value="0.33"/>
          <mosqSurvivalFeedingCycleProbability value="0.611"/>
          <availabilityVariance value="0"/>
          <mosqProbBiting mean="0.95" variance="0"/>
          <mosqProbFindRestSite mean="0.95" variance="0"/>
          <mosqProbResting mean="0.99" variance="0"/>
          <mosqProbOvipositing value="0.88"/>
          <mosqHumanBloodIndex value=".90"/>
        </mosq>
        <nonHumanHosts name="unprotectedAnimals">
          <mosqRelativeEntoAvailability value="1.0"/>
          <mosqProbBiting value="0.95"/>
          <mosqProbFindRestSite value="0.95"/>
          <mosqProbResting value="0.99"/>
        </nonHumanHosts>
</anopheles>
"""

class AnophelesSnippetTest(TestCase):
    def setUp(self):
        self.snippet = AnophelesSnippet.objects.create(anopheles=SNIPPET)

    def test_str(self):
        self.assertEqual(str(self.snippet), "funestus")

    def test_name_1(self):
        self.assertEqual(self.snippet.name, "funestus")

    def test_name_2(self):
        snippet = AnophelesSnippet.objects.create(anopheles="")
        self.assertEqual(snippet.name, "Invalid xml snippet")

    def test_name_3(self):
        snippet = AnophelesSnippet.objects.create(anopheles="<xml></xml>")
        self.assertEqual(snippet.name, "Unnamed anopheles snippet")
