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

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls.base import reverse

from website.apps.ts_om.models import Scenario
from website.notification import set_notification, SUCCESS


@login_required
def delete_scenario_view(request, scenario_id):
    scenario = get_object_or_404(Scenario, id=scenario_id)
    if scenario.user != request.user:
        raise PermissionDenied

    scenario.deleted = not scenario.deleted
    scenario.save()
    set_notification(request, "Scenario %s successfully deleted" % scenario.name, SUCCESS)
    return HttpResponseRedirect(reverse("ts_om.list"))
