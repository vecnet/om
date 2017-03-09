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
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from lxml import etree
from lxml.etree import XMLSyntaxError

from website.apps.ts_om.models import Scenario


@login_required
def duplicate_scenario_view(request, scenario_id):

    scenario = get_object_or_404(Scenario, user=request.user, id=int(scenario_id))

    xml = scenario.xml

    try:
        tree = etree.parse(StringIO(str(xml)))
    except XMLSyntaxError:
        # Copy xml document as is
        pass
    else:
        tree.getroot().set('name', scenario.name + " (duplicate)")
        xml = etree.tostring(tree.getroot(), encoding='UTF-8')

    new_scenario = Scenario.objects.create(
        xml=xml,
        start_date=scenario.start_date,
        user=request.user,
        baseline=scenario.baseline,
        description=scenario.description,
    )

    return HttpResponseRedirect(reverse('ts_om.summary2', kwargs={'scenario_id': new_scenario.id}))