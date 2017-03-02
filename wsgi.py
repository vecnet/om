"""
WSGI config for the project (not default Django wsgi.py)

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application


try:
    # Import stuff from config_local.py (if any)
    from config_local import *
except ImportError:
    pass

try:
    # If settings_module is not defined in config_local.py, default to website.settings.production
    from config_local import settings_module
except ImportError:
    settings_module = "website.settings.production"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

application = get_wsgi_application()
