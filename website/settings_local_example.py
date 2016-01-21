# Example server configuration
# Copy this file to setting_local.py

from django_auth_pubtkt.views import redirect_to_sso
from django.conf.urls import url
LOGIN_URL = "/sso/"
TKT_AUTH_LOGIN_URL = "https://www.vecnet.org/index.php/sso-login"
TKT_AUTH_PUBLIC_KEY = '/etc/httpd/conf/sso/tkt_pubkey_dsa.pem'
URLS_SSO = [url(r'^sso/', redirect_to_sso),]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django_auth_pubtkt.DjangoAuthPubtkt',
    'django.contrib.messages.middleware.MessageMiddleware',
)