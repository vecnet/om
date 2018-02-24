from django.conf import settings
import website

def app_env(request):
    """ This function defines login and logout pages.
    If we are running in production enviroment, use auth_pubtkt.
    In dev enviroment, use local django auth system
    """
    env = {
        "FOOTER_TEMPLATE": settings.FOOTER_TEMPLATE,
        "HEADER_TEMPLATE": settings.HEADER_TEMPLATE,
        "LOGIN_URL": settings.LOGIN_URL,
        "REDIRECT_FIELD_NAME": getattr(settings, 'REDIRECT_FIELD_NAME', 'next'),
        "LOGOUT_URL": settings.LOGOUT_URL
    }
    # if hasattr(settings, "SERVER_MAINTENANCE_MESSAGE"):
    #      env["SERVER_MAINTENANCE_MESSAGE"] = settings.SERVER_MAINTENANCE_MESSAGE
    return env

def site_url(request):
    """ Add SITE_URL variable to the context """
    return {"SITE_URL": website.get_site_url()}
