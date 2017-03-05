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