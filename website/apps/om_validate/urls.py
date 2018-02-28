from django.conf.urls import url
from .views import validate_view

urlpatterns = [
   url(r'^validate/$', validate_view, name='validate'),
]
