from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from website.apps.ts_om.views.ScenarioSummaryView2 import update_summary_form
from website.apps.ts_om.views.ScenarioView import download_experiment_scenario, save_scenario
from website.apps.ts_om.views.download_scenario_xml_view import download_scenario_xml_view
from website.apps.ts_om.views.duplicate_scenario_view import duplicate_scenario_view
from website.apps.ts_om.views.update_scenario_view import update_scenario_view
from website.apps.ts_om_experiment.views.ExperimentRunView import get_sim_group_status
from website.apps.ts_om.views.submit_scenarios_view import submit_scenarios
from website.apps.ts_om.views.ScenarioSummaryView2 import ScenarioSummaryView2
from website.apps.ts_om.views.ScenarioAdvancedView import ScenarioAdvancedView
from website.apps.ts_om.views.ScenarioListView import ScenarioListView
from website.apps.ts_om.views.ScenarioValidationView import ScenarioValidationView
from website.apps.ts_om.views.ScenarioStartView import ScenarioStartView
from website.apps.ts_om.views.ScenarioDeleteView import ScenarioDeleteView

urlpatterns = patterns('',
   url(r'^$', login_required(ScenarioListView.as_view()), name='ts_om.list'),
   url(
       r'^(?P<scenario_id>.+)/experiment/(?P<index>.+)/scenario/download/$',
       download_experiment_scenario,
       name='ts_om.download_experiment_scenario'
   ),
   url(r'^restValidate/$', ScenarioValidationView.as_view(), name='ts_om.restValidate'),
   url(r'^start/$', login_required(ScenarioStartView.as_view()), name='ts_om.start'),
   url(r'^(?P<scenario_id>.+)/summary2/$', ScenarioSummaryView2.as_view(), name='ts_om.summary2'),
   url(r'^(?P<scenario_id>.+)/advanced/$', ScenarioAdvancedView.as_view(), name='ts_om.advanced'),
   url(r'^deleteScenario/$', ScenarioDeleteView.as_view(), name='ts_om.deleteScenario'),
   url(r'^(?P<scenario_id>.+)/duplicate/$', duplicate_scenario_view, name='ts_om.duplicate'),
   url(r'^(?P<scenario_id>.+)/download/$', download_scenario_xml_view, name='ts_om.download'),
   url(r'^update/$', update_scenario_view, name='ts_om.scenario.update'),
   url(r'^(?P<scenario_id>.+)/save/$', save_scenario, name='ts_om.save'),
   url(r'^scenarios/submit/$', submit_scenarios, name='ts_om.submit'),
   url(r'^utilities/$', TemplateView.as_view(template_name="ts_om/utilities.html"), name='ts_om.utilities'),
   url(
       r'^(?P<experiment_id>.+)/experiment/run/(?P<run_type>\w+)/status/$',
       get_sim_group_status,
       name='ts_om.run_status'
   ),
   url(r'^(?P<scenario_id>.+)/summary/update/form/$', update_summary_form, name='ts_om.summary.update.form'),
)
