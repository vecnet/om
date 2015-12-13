from django.conf.urls import patterns, url

from website.apps.ts_om_viz.views.UploadView import UploadView
from website.apps.ts_om_viz.views.SimulationView import SimulationView, get_cts_data, get_survey_data
from website.apps.ts_om_viz.views.download import download


urlpatterns = patterns(
    'ts_om_viz.views',
    #########################################################################################
    # Main views
    #########################################################################################
    # Index view
    url(r'^$', UploadView.as_view(), name='ts_om_viz.UploadView'),
    # Simulation results view
    url(r'^sim/(?P<id>\d+)/$', SimulationView.as_view(), name='ts_om_viz.SimulationView'),
    # Simulation Group results view
    # url(r'^sim/group/(?P<id>\d+)/$', SimGroupView.as_view(), name='GroupView'),

    #########################################################################################
    # Endpoints for AJAX calls
    #########################################################################################

    # Download scenario files (both input and output)
    url(r'^download/(?P<simulation_id>\d+)/(?P<name>.+)', download, name="ts_om_viz.download"),
    url(r'^sim/data/survey/(?P<sim_id>\d+)/(?P<measure_id>\d+)/(?P<bin_number>\w+)/$',
        get_survey_data,
        name="ts_om_viz.get_survey_data"),
    url(r'^sim/data/cts/(?P<sim_id>\d+)/(?P<measure_name>.+)/$', get_cts_data, name="ts_om_viz.get_cts_data"),

    # data fetching urls for ajax calls for output through simulation data service
    # url(r'^sim/group/data/$', get_output_valueset_sim_group, name="results_subGroupID_sim_group"),
    # url(r'^sim/group/data/(?P<sim_id>\d+)/(?P<third_dimension>\w+)/(?P<measure>\d+)/$',
    #     get_output_valueset_sim_group,
    #     name="results_subGroupID_sim_group"),
    # # data fetching urls for ajax calls for continuous output
    # url(r'^sim/group/cts_data/$', get_ctsout_valueset_sim_group, name="results_continuous_sim_group"),
    # url(r'^sim/group/cts_data/(?P<sim_id>\d+)/(?P<index>\d+)/$',
    #     get_ctsout_valueset_sim_group,
    #     name="results_continuous_sim_group"),
)
