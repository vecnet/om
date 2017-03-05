# Copyright (C) 2016, University of Notre Dame
# All rights reserved
from StringIO import StringIO

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from lxml import etree

from website.apps.ts_om.models import Scenario


@login_required
def download_scenario_xml_view(request, scenario_id):

    scenario = get_object_or_404(Scenario, user=request.user, id=int(scenario_id))

    f = StringIO(str(scenario.xml))
    try:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(f, parser)
        xml = etree.tostring(tree.getroot(), encoding='UTF-8', pretty_print=True)
    except etree.XMLSyntaxError:
        xml = scenario.xml

    return HttpResponse(xml)