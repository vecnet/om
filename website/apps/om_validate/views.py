import string
import random
import os
import glob
import subprocess
import json
import logging

from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from lxml import etree

from website.apps.ts_om.check import check_url, check_dir

logger = logging.getLogger('prod_logger')


@csrf_exempt
def validate(request):
    logger.info("om_validate service started")
    logger.info("user: %s" % request.user)
    fileNew = request.read()
    om_dir = check_url(getattr(settings, "OPENMALARIA_EXEC_DIR", None), "openmalaria")
    scenarios_dir = check_dir(getattr(settings, "TS_OM_SCENARIOS_DIR", None))
    return_code = 0
    out = None
    data = {}

    os.chdir(om_dir)

    schema = []
    for f in glob.glob(om_dir + '*.xsd'):
        schema.append(f)

    xmlSchemaDoc = etree.parse(schema[0])
    xmlSchema = etree.XMLSchema(xmlSchemaDoc)

    try:
        tree = etree.fromstring(fileNew)
    except etree.ParseError as e:
        return_code = -1
        out = ""
        for entry in e.error_log:
            out += entry.message + "\n"

    if not out:
        try:
            xmlSchema.assertValid(tree)
        except etree.DocumentInvalid as e:
            return_code = -1
            out = ""
            for entry in e.error_log:
                out += entry.message + "\n"
        except etree.XMLSchemaValidateError as e:
            return_code = -1
            out = ""
            for entry in e.error_log:
                out += entry.message + "\n"

    filename = None
    if not out:
        logger.info("scenarios_dir: %s" % scenarios_dir)
        if not os.path.isdir(scenarios_dir):
            logger.info("Created %s" % scenarios_dir)
            os.mkdir(scenarios_dir)
        filename = os.path.join(scenarios_dir, 'scenario_' + ''.join(random.sample(string.lowercase+string.digits,10)) + ".xml")
        logger.info("Filename: %s" % filename)
        with open(filename, 'w') as destination:
            destination.write(fileNew)

        if os.name == "nt":
            cmd = ['openMalaria.exe', '--scenario', filename, '--validate-only']
        else:
            cmd = ['./openMalaria', '--scenario', filename, '--validate-only']
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            return_code = e.returncode
            out = e.output

    # Remove temp file
    if filename:
        os.unlink(filename)

    logger.info("Return code: %s" % return_code)
    data['result'] = return_code
    data['om_output'] = out.split("\n")

    return HttpResponse(json.dumps(data), mimetype="application/json")
