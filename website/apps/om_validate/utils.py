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
import logging
import subprocess

from django.conf import settings
from django.utils.crypto import get_random_string
from lxml import etree

logger = logging.getLogger(__name__)


def get_xml_validation_errors(xml, skip_openmalaria_validation=False):
    """ Validate if the xml document is a valid OpenMalaria scenario. Return a list or errors or None if valid.
    By default checks whether the syntax is correct, validates against OpenMalaria schema document and
    runs openmalaria executable with --validate-only flag (the latter can be skipped)

    :param xml:
    :param skip_openmalaria_validation: If True, skip running openmalaria to validate the scenario
    :return:
    """
    # Check if document is well-formed
    errors = []
    # result = xml_schema.validate(tree)
    parser = etree.XMLParser()
    try:
        tree = etree.XML(xml, parser)
    except etree.ParseError as e:
        logger.debug("Parse error: %s" % e)
        # Parsers have an error_log property that lists the errors and warnings of the last parser run:
        for entry in parser.error_log:
            errors.append(entry.message)
        return errors

    # Check against scenario32.xsd schema
    # It is possible to combine this with checking whether the document is well-formed or not,
    # but errors messages are more meaningful this way
    om_dir = os.path.dirname(settings.OM_EXECUTABLE)

    xmlSchemaDoc = etree.parse(os.path.join(om_dir, "scenario_32.xsd"))
    xml_schema = etree.XMLSchema(xmlSchemaDoc)
    parser = etree.XMLParser(schema=xml_schema)

    try:
        tree = etree.XML(xml, parser)
    except etree.ParseError as e:
        logger.debug("Parse error: %s" % e)
        # Parsers have an error_log property that lists the errors and warnings of the last parser run:
        for entry in parser.error_log:
            errors.append(entry.message)
        return errors

    # Check using build-in OpenMalaria validation
    if not skip_openmalaria_validation:
        errors = validate_openmalaria(xml)
        if errors:
            return errors

    return None


def validate_openmalaria(xml):
    """ Validate XML using built-in openmalaria validation tool (--validate-only) """
    scenarios_dir = os.path.join(settings.MEDIA_ROOT, "tmp")
    om_dir = os.path.dirname(settings.OM_EXECUTABLE)

    logger.info("scenarios_dir: %s" % scenarios_dir)
    if not os.path.isdir(scenarios_dir):
        try:
            os.mkdir(scenarios_dir)
        except Exception as e:
            logger.critical("MEDIA_ROOT directory problem: %s" % e)
            return ["MEDIA_ROOT problem: %s" % e]
        logger.info("Created %s" % scenarios_dir)

    filename = os.path.join(
        scenarios_dir,
        'scenario_validation_%s.xml' % get_random_string()
    )

    logger.debug("Filename: %s" % filename)
    try:
        with open(filename, 'w') as fp:
            fp.write(xml)
    except Exception as e:
        logger.critical("Can't write file %s: %s" % (filename, e))
        return ["Can't write file: %s" % e]

    cmd = [settings.OM_EXECUTABLE, '--scenario', filename, '--validate-only']

    return_code = 0
    errors = None
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, cwd=om_dir)
    except subprocess.CalledProcessError as e:
        # Note that -11 means "Segmentation fault"
        # Also, http://stackoverflow.com/questions/18731791/determining-if-a-python-subprocess-segmentation-faults
        return_code = e.returncode
        out = e.output
        # out.split("\n")
        errors = [line.strip() for line in out.split("\n")]
        if return_code == -11:
            errors.append("Segmentation fault")
            logger.error("Segmentation fault when validating scenario")
        logger.info("subprocess error, return code: %s" % return_code)
    except Exception as e:
        # The system cannot find the file specified and so on
        errors = ["%s" % e]

    os.unlink(filename)

    return errors
