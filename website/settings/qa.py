from .base import *


ALLOWED_HOSTS = [
    'om-qa.vecnet.org',
]


SECRET_KEY = get_env_variable("SECRET_KEY")

DATABASES = {
    'default': {
        'ENGINE': get_env_variable("DATABASE_ENGINE"),
        'NAME': get_env_variable("DATABASE_NAME"),
        'USER': get_env_variable("DATABASE_USER"),
        'PASSWORD': get_env_variable("DATABASE_PASSWORD"),
        'HOST': get_env_variable("DATABASE_HOST"),
        'PORT': get_env_variable("DATABASE_PORT"),
    }
}

# SMTP server configuration
EMAIL_HOST = "smtp.nd.edu"
EMAIL_PORT = 25
EMAIL_USE_TLS = True

PYTHON_EXECUTABLE = "/opt/venvs/om-qa.vecnet.org/bin/python"
SIM_SERVICE_LOCAL_OM_EXECUTABLE = "/opt/portal/om-qa.vecnet.org/binaries/om/openMalaria"

LOGIN_URL = "/sso/"
LOGOUT_URL="https://www.vecnet.org/index.php/log-out"
TKT_AUTH_LOGIN_URL = "https://www.vecnet.org/index.php/sso-login"
TKT_AUTH_PUBLIC_KEY = '/etc/httpd/conf/sso/tkt_pubkey_dsa.pem'
