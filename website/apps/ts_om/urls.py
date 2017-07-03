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
from django.contrib.auth.decorators import login_required

from website.apps.ts_om.views.ScenarioDeleteView import ScenarioDeleteView
from website.apps.ts_om.views.ScenarioListView import ScenarioListView
from website.apps.ts_om.views.ScenarioStartView import ScenarioStartView
from website.apps.ts_om.views.ScenarioValidationView import ScenarioValidationView
from website.apps.ts_om.views.download_scenario_xml_view import download_scenario_xml_view
from website.apps.ts_om.views.duplicate_scenario_view import duplicate_scenario_view
from website.apps.ts_om.views.get_scenario_status_view import get_scenario_status_view
from website.apps.ts_om.views.submit_scenarios_view import submit_scenarios
from website.apps.ts_om.views.update_scenario_view import update_scenario_view
from website.apps.ts_om_experiment.views.ExperimentRunView import get_sim_group_status

urlpatterns = [
    url(r'^$', login_required(ScenarioListView.as_view()), name='ts_om.list'),

    url(r'^restValidate/$', ScenarioValidationView.as_view(), name='ts_om.restValidate'),
    url(r'^start/$', login_required(ScenarioStartView.as_view()), name='ts_om.start'),
    url(r'^deleteScenario/$', ScenarioDeleteView.as_view(), name='ts_om.deleteScenario'),
    url(r'^(?P<scenario_id>.+)/duplicate/$', duplicate_scenario_view, name='ts_om.duplicate'),
    url(r'^(?P<scenario_id>.+)/download/$', download_scenario_xml_view, name='ts_om.download'),
    url(r'^update/$', update_scenario_view, name='ts_om.scenario.update'),
    url(r'^get_scenario_status/$', get_scenario_status_view, name='ts_om.status'),
    url(r'^scenarios/submit/$', submit_scenarios, name='ts_om.submit'),
    url(
       r'^(?P<experiment_id>.+)/experiment/run/(?P<run_type>\w+)/status/$',
       get_sim_group_status,
       name='ts_om.run_status'
   ),
]
