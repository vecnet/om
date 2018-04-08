from .base import *


ADMINS = [
    ('Alex', 'alex.vyushkov@gmail.com'),
]

ALLOWED_HOSTS = [
    'om-qa.vecnet.org',
]

SECRET_KEY = get_env_variable("SECRET_KEY")

DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql_psycopg2",
        'NAME': get_env_variable("DATABASE_NAME"),
        'USER': get_env_variable("DATABASE_USER"),
        'PASSWORD': get_env_variable("DATABASE_PASSWORD"),
        'HOST': "127.0.0.1",
        'PORT': "5432",
    }
}

# SMTP server configuration
EMAIL_HOST = "smtp.nd.edu"
EMAIL_PORT = 25
EMAIL_USE_TLS = True
# SMTP Backend: the backend to use for sending emails.
# Overriding development settings (Console backend)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# The email address that error messages come from, such as those sent to ADMINS and MANAGERS.
# Used by mail_managers function
SERVER_EMAIL = "VecNet OpenMalaria Portal <avyushko@nd.edu>"

PYTHON_EXECUTABLE = "/opt/venvs/om-qa.vecnet.org/bin/python"
OM_EXECUTABLE = "/opt/portal/om-qa.vecnet.org/binaries/om/openMalaria"

LOGIN_URL = "/sso/"
LOGOUT_URL="https://www.vecnet.org/index.php/log-out"
TKT_AUTH_LOGIN_URL = "https://www.vecnet.org/index.php/sso-login"
TKT_AUTH_PUBLIC_KEY = '/etc/httpd/conf/sso/tkt_pubkey_dsa.pem'

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('django_auth_pubtkt.middleware.DjangoAuthPubtkt',)

# CRONTAB_COMMENT used for marking the added contab-lines for removing, default value includes project name
# to distinguish multiple projects on the same host and user
CRONTAB_COMMENT = "qa"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),
            'formatter': 'withtimestamp'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'WARNING',
            'propagate': True,
        },
        'website': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propogate': True,
        },
        'sim_services_local': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propogate': True,
        }
    },
    "formatters": {
        "simple": {
           "format": "%(levelname)s: [%(name)s:%(lineno)s] %(message)s"
        },
        "withtimestamp": {
           "format": "%(levelname)s:[%(asctime)s] [%(name)s:%(lineno)s] %(message)s"
        }
    }
}

# Security options
# https://docs.djangoproject.com/en/1.10/ref/settings/#std:setting-CSRF_COOKIE_AGE
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False  # Don't set to True just yet - ajaxSetup in common.js depends on that cookie
CSRF_COOKIE_AGE = 60480  # One week
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# Frames as used on this website, so setting to the 'SAMEORIGIN'
X_FRAME_OPTIONS = "SAMEORIGIN"

# Unless your site should be available over both SSL and non-SSL connections, you may want to either
# set this setting True or configure a load balancer or reverse-proxy server to redirect all connections to HTTPS.
SECURE_SSL_REDIRECT = True

# Set the Anti-MIME-Sniffing header X-Content-Type-Options to 'nosniff'.
# This prevents older versions of Internet Explorer and Chrome from performing MIME-sniffing on the response body,
# potentially causing the response body to be interpreted and displayed as a content type other than the declared
# content type. Current (early 2014) and legacy versions of Firefox will use the declared content type (if one is set),
# rather than performing MIME-sniffing.
SECURE_CONTENT_TYPE_NOSNIFF = True

# Pages will be served with an 'x-xss-protection: 1; mode=block' header to to activate the browser's
# XSS filtering and help prevent XSS attacks
SECURE_BROWSER_XSS_FILTER = True

# Site URL
SITE_URL = "https://om-qa.vecnet.org"

try:
    # Optional settings specific to the local system (for example, custom
    # settings on a developer's system).  The file "settings_local.py" is
    # excluded from version control.
    from .settings_local import *
except ImportError:
    pass
