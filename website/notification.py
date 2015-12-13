# enable Django logging for this module
import logging
from django.http.request import HttpRequest
import warnings

logger = logging.getLogger(__name__)

SUCCESS = "alert-success"
DANGER = "alert-danger"
WARNING = "alert-warning"
INFO = "alert-info"


def set_notification(session, message, alert_type):

    """ Set notification that will be displayed in {% notifications %} templatetag when page is rendered

    This function should be call in a Django view. Session object is normally available as request.session
    (provided that sessions are enabled in your Django project).
    Bootstrap alert class is used (<div class="alert {{ notification.type }}">)

    :param session: Django session object (request.session) or HttpRequest object
    :param message: Message to be show
    :type message: str
    :param alert_type: alert class - alert-cuess
    :type alert_type: "alert-success", "alert-error", "alert", "alert-info"
    """

    # Preparing for switching to Django HttpRequest
    if isinstance(session, HttpRequest):
        session = session.session
    else:
        warnings.warn("Using Django session variable is depricated, pass HttpRequest object to set_notification function instead", RuntimeWarning)  # noqa

    if not session.__contains__("notifications"):
        session["notifications"] = []
    session["notifications"].append({"message": message, "type": alert_type})
    logger.debug("Webpage notification: [%s] %s" % (alert_type, message))


set_notification.SUCCESS = "alert-success"
set_notification.DANGER = "alert-danger"
set_notification.WARNING = "alert-warning"
set_notification.INFO = "alert-info"
