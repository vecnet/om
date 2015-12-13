from django.conf.urls import include, patterns

from .rest_api.api import v1_api


urlpatterns = patterns('',
                       (r'^api/', include(v1_api.urls)),
                       )
