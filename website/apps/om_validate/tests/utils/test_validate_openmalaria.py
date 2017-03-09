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
from django.test.utils import override_settings

from website.apps.om_validate.utils import validate_openmalaria


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files")

def get_xml(filename="scenario.xml"):
    with open(os.path.join(DATA_DIR, filename)) as fp:
        xml = fp.read()
    return xml


class ValidateOpenmalariaTests(TestCase):
    @override_settings(OM_EXECUTABLE="/non-existent/executable")
    def test_incorrect_executable(self):
        errors = validate_openmalaria("<>")
        # Error message is different on different platforms
        # os.name == "nt" : [Errno 2] No such file or directory: '/non-existent'
        # "linux": [Error 2] The system cannot find the file specified
        self.assertIsNotNone(errors[0])
        self.assertNotEqual(errors[0], "")
        self.assertEqual(len(errors), 1)

    def test_broken_xml_1(self):
        # WARNING: this test runs openmalaria in background
        errors = validate_openmalaria("<>")
        self.assertIn("XSD error: instance document parsing failed", errors[1])
        self.assertEqual(len(errors), 4)

    def test_broken_xml_2(self):
        # WARNING: this test runs openmalaria in background
        # Note that scenario_om_error.xml should pass schema validation, but fails openmalaria validation
        # See diff with scenario.xml to see what's wrong
        # (missing <anopheles mosquito="gambiae1"> in intervention description)
        errors = validate_openmalaria(get_xml("scenario_om_error.xml"))
        self.assertIn("Error: Unrecognised survey option: \"nHost11\"", errors[1])
        self.assertEqual(len(errors), 4)

    @override_settings(MEDIA_ROOT="/non-existent/directory/")
    def test_bad_media_root(self):
        # WARNING: this test tried to create a directory in random place (/non-existent/directory/)
        # It normally should fail, but if not - additional clean up might be required
        errors = validate_openmalaria(get_xml("scenario.xml"))
        self.assertIn("MEDIA_ROOT problem", errors[0])

    def test_success(self):
        # WARNING: this test runs openmalaria in background
        # Note that scenario_.xml should pass all checks, including openmalaria validation
        errors = validate_openmalaria(get_xml("scenario.xml"))
        self.assertIsNone(errors)
