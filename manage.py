#!/usr/bin/env python
import os
import sys

try:
    from config_local import settings_module
    settings_module_message = "as defined in config_local.py file. DJANGO_SETTINGS_MODULE is ignored."
except ImportError:
    settings_module = "website.settings.local"
    settings_module_message = ""

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

    print("manage.py: Using settings: %s %s" % (os.environ.get("DJANGO_SETTINGS_MODULE"), settings_module_message))
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
