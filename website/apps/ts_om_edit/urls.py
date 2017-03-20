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

from django.conf.urls import patterns, url

from website.apps.ts_om_edit.views.ScenarioSummaryView import ScenarioSummaryView
from .views.ScenarioMonitoringView import ScenarioMonitoringView
from .views.ScenarioDemographyView import ScenarioDemographyView
from .views.ScenarioHealthSystemView import ScenarioHealthSystemView
from .views.ScenarioEntomologyView import ScenarioEntomologyView
from .views.ScenarioInterventionsView import ScenarioInterventionsView
from .views.ScenarioDeploymentsView import ScenarioDeploymentsView

from website.apps.ts_om_edit.views.ScenarioMonitoringView import update_monitoring_form
from .views.ScenarioDemographyView import update_demography_form
from .views.ScenarioHealthSystemView import update_healthsystem_form
from .views.ScenarioEntomologyView import update_entomology_form
from .views.ScenarioInterventionsView import update_interventions_form
from website.apps.ts_om_edit.views.ScenarioDeploymentsView import update_deployments_form
from website.apps.ts_om_edit.views.ScenarioEntomologyView import delete_species_from_scenario_view


urlpatterns = patterns('',
       url(r'^(?P<scenario_id>.+)/summary/$', ScenarioSummaryView.as_view(), name='ts_om.summary'),
       url(r'^(?P<scenario_id>.+)/monitoring/$', ScenarioMonitoringView.as_view(), name='ts_om.monitoring'),
       url(r'^(?P<scenario_id>.+)/demography/$', ScenarioDemographyView.as_view(), name='ts_om.demography'),
       url(r'^(?P<scenario_id>.+)/healthsystem/$', ScenarioHealthSystemView.as_view(),
           name='ts_om.healthsystem'),
       url(r'^(?P<scenario_id>.+)/entomology/$', ScenarioEntomologyView.as_view(), name='ts_om.entomology'),
       url(r'^(?P<scenario_id>.+)/interventions/$', ScenarioInterventionsView.as_view(),
           name='ts_om.interventions'),
       url(r'^(?P<scenario_id>.+)/deployments/$', ScenarioDeploymentsView.as_view(), name='ts_om.deployments'),


       url(r'^(?P<scenario_id>.+)/monitoring/update/form/$', update_monitoring_form,
           name='ts_om.monitoring.update.form'),
       url(r'^(?P<scenario_id>.+)/demography/update/form/$', update_demography_form,
           name='ts_om.demography.update.form'),
       url(r'^(?P<scenario_id>.+)/healthsystem/update/form/$', update_healthsystem_form,
           name='ts_om.healthsystem.update.form'),
       url(r'^(?P<scenario_id>.+)/entomology/update/form/$', update_entomology_form,
           name='ts_om.entomology.update.form'),
       url(r'^(?P<scenario_id>.+)/interventions/update/form/$', update_interventions_form,
           name='ts_om.interventions.update.form'),
       url(r'^(?P<scenario_id>.+)/deployments/update/form/$', update_deployments_form,
           name='ts_om.deployments.update.form'),

       url(r'^remove_species_from_scenario/(?P<scenario_id>.+)/(?P<species>.+)/', delete_species_from_scenario_view, name='ts_om.remove_species_from_scenario'),  # noqa

       )
