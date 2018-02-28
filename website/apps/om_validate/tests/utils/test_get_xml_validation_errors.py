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

    def test_unicode_1(self):
        errors = get_xml_validation_errors("<xml></xml>")
        self.assertEqual(
            errors,
            ["Element 'xml': No matching global declaration available for the validation root."]
        )

    def test_unicode_2(self):
        # Make sure this doesn't happen:
        # ValueError: Unicode strings with encoding declaration are not supported.
        # Please use bytes input or XML fragments without declaration.

        errors = get_xml_validation_errors("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<om:scenario xmlns:om="http://openmalaria.org/schema/scenario_32" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" name="South Bend, Indiana - 1000 people" schemaVersion="32" xsi:schemaLocation="http://openmalaria.org/schema/scenario_32 scenario_32.xsd">
""")
        self.assertEqual(
            errors,
            ["Premature end of data in tag scenario line 2"]
        )

    def test_unicode_success(self):
        # For some reason in some cases get_xml_validation_errors get unicode, not string in production environment
        result = get_xml_validation_errors(str(get_xml()))
        self.assertEqual(result, None)

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
            ['attributes construct error', "Couldn't find end of Start Tag group line 5"]
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
        self.assertIn("Error: Unrecognised survey option: \"nHost11\"", errors[1])
        self.assertEqual(len(errors), 4)

    def test_success(self):
        result = get_xml_validation_errors(get_xml())
        self.assertEqual(result, None)