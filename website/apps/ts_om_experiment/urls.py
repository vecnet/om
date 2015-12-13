from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from views.ExperimentUploadView import ExperimentUploadView
from views.ExperimentValidateView import ExperimentValidateView
from views.ExperimentRunView import ExperimentRunView
from website.apps.ts_om_experiment.views.ExperimentRunView import get_sim_group_status, download_experiment_zip

urlpatterns = patterns('',
                       url(r'^experiment/upload/$', login_required(ExperimentUploadView.as_view()),
                           name='ts_om.upload'),
                       url(r'^experiment/validate/$', ExperimentValidateView.as_view(), name='ts_om.validate'),
                       url(r'^(?P<experiment_id>.+)/experiment/run/(?P<run_type>\w+)/$', ExperimentRunView.as_view(),
                           name='ts_om.run'),
                       url(r'^(?P<experiment_id>.+)/experiment/download/(?P<run_type>\w+)/$', download_experiment_zip,
                           name='ts_om.download_experiment'),
                       url(r'^(?P<experiment_id>.+)/experiment/run/(?P<run_type>\w+)/status/$', get_sim_group_status,
                           name='ts_om.run_status'),
                       )
