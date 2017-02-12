"""
WSGI config for the project

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

try:
    from config_local import settings_module
except ImportError:
    settings_module = "website.settings.prod"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")

application = get_wsgi_application()
