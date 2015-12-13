# Copyright (C) 2015, University of Notre Dame
# All rights reserved


from django.conf.urls import patterns, url
from website.apps.umbrella.views import generate_umbrella_specification_view

urlpatterns = patterns('',
                       url(r'^download_umbrella_spec/(?P<scenario_id>.+)/', generate_umbrella_specification_view,
                           name="umbrella.umbrella_spec")
                       )
