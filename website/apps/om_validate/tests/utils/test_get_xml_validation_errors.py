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

import os
from django.test.testcases import TestCase

from website.apps.om_validate.utils import get_xml_validation_errors

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files")

def get_xml(filename="scenario.xml"):
    with open(os.path.join(DATA_DIR, filename)) as fp:
        xml = fp.read()
    return xml

class GetXmlValidationErrorsTest(TestCase):
    def test(self):
        result = get_xml_validation_errors("123")
        print result

    def test_syntax_error_1(self):
        errors = get_xml_validation_errors("<xml></xml>")
        self.assertEqual(
            errors,
            ["Element 'xml': No matching global declaration available for the validation root."]
        )

    def test_syntax_error_2(self):
        errors = get_xml_validation_errors(get_xml("scenario_bad.xml"))
        self.assertEqual(
            errors,
            [u'attributes construct error', u"Couldn't find end of Start Tag group line 5"]
        )

    def test_schema_error_1(self):
        errors = get_xml_validation_errors(get_xml("scenario_schema_error.xml"))
        self.assertEqual(
            errors[0],
            "Element '{http://openmalaria.org/schema/scenario_32}scenario': Missing child element(s). "
            "Expected is one of ( demography, pharmacology )."
        )
        self.assertEqual(len(errors), 1)

    def test_om_error(self):
        # WARNING: this test runs openmalaria in background
        # Note that scenario_om_error.xml should pass schema validation, but fails openmalaria validation
        # See diff with scenario.xml to see what's wrong
        # (missing <anopheles mosquito="gambiae1"> in intervention description)
        errors = get_xml_validation_errors(get_xml("scenario_om_error.xml"))
        self.assertIn("Error: Intervention \"\" has a no description for vector species \"gambiae1\"", errors[1])
        self.assertEqual(len(errors), 5)

    def test_success(self):
        result = get_xml_validation_errors(get_xml())
        self.assertEqual(result, None)