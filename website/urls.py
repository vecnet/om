""" URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import TemplateView, RedirectView

from website.views import test_http_code_500

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r'^$', RedirectView.as_view(url='/ts_om/', permanent=False), name="index"),
    # robots.txt is implemented as a template because Django can't seem to serve a static file from urls.py
    url(r'^robots.txt$', TemplateView.as_view(template_name="robots.txt")),
    # Please refer to https://docs.djangoproject.com/en/1.8/topics/auth/default/#using-the-views
    # for additional information about using django.contrib.auth.urls
    url(r'^auth/', include('django.contrib.auth.urls')),
    url(r'^test_500/$', test_http_code_500, name="test_http_code_500"),
    url(r'^ts_om/', include('website.apps.ts_om.urls')),
    url(r'^ts_om_edit/', include('website.apps.ts_om_edit.urls')),
    url(r'^ts_om_viz/', include('website.apps.ts_om_viz.urls')),
    url(r'^validate/', include('website.apps.om_validate.urls')),
    url(r'^big_brother/', include('website.apps.big_brother.urls')),
]

try:
    # If django_auth_pubtkt is installed, add sso/ to url patterns
    from django_auth_pubtkt.views import redirect_to_sso
    urlpatterns.append(url(r'^sso/', redirect_to_sso))
except ImportError:
    pass


try:
    # If django-registration is installed, add registration urls to url patterns
    import registration.backends.simple.urls

    urlpatterns.append(url(r'^accounts/', include('registration.backends.simple.urls')))
except ImportError:
    pass

# handler404 = TemplateView.as_view(template_name="404.html")
