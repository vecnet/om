from django.conf.urls import url

from website.apps.big_brother.views import tracking_code_view
from website.apps.email.utils.tracking_code_callback import tracking_code_callback

urlpatterns = [
    url(
        r"^img/(?P<tracking_code>.*)/$",
        tracking_code_view,
        name="email.track",
        kwargs={"callback": tracking_code_callback}
    ),
]
