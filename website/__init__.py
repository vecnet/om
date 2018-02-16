from django.apps import AppConfig
# That import below is required to activate signal handlers for this application
import website.signals
# Can't define get_site_url here - override_settings in tests doesn't work if we do
from website.utils import get_site_url

# Please refer to https://docs.djangoproject.com/en/dev/ref/applications/#for-application-authors
# for additional details
default_app_config = 'website.WebsiteConfig'


class WebsiteConfig(AppConfig):
    name = 'website'
