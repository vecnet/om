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

from django.conf.urls import url

from website.apps.ts_om_viz.views.SimulationView import SimulationView
from website.apps.ts_om_viz.views.get_cts_data_view import get_cts_data_view
from website.apps.ts_om_viz.views.get_survey_data_view import get_survey_data_view
from website.apps.ts_om_viz.views.download_view import download_view


urlpatterns = [
    # Simulation results view
    url(r'^sim/(?P<id>\d+)/$', SimulationView.as_view(), name='ts_om_viz.SimulationView'),

    # Endpoints for AJAX calls
    # Download scenario files (both input and output)
    url(r'^download/(?P<simulation_id>\d+)/(?P<name>.+)', download_view, name="ts_om_viz.download"),
    url(r'^sim/data/survey/(?P<sim_id>\d+)/(?P<measure_id>\d+)/(?P<bin_number>\w+)/$',
        get_survey_data_view,
        name="ts_om_viz.get_survey_data"),
    url(r'^sim/data/cts/(?P<sim_id>\d+)/(?P<measure_name>.+)/$', get_cts_data_view, name="ts_om_viz.get_cts_data"),
]
