# -*- coding: utf-8 -*-
#
# This file is part of the VecNet OpenMalaria Portal.
# For copyright and licensing information about this package, see the
# NOTICE.txt and LICENSE.txt files in its top-level directory; they are
# available at https://github.com/vecnet/om
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0.  If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
import os

from django.http.response import HttpResponse

from website.apps.big_brother.models import TrackingCode

logger = logging.getLogger(__name__)
static_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))), "static", "big_brother")


def tracking_code_view(request, tracking_code, callback=None):
    """ This view is to track which invitation emails were read by users """
    with open(os.path.join(static_dir, "1x1.png"), "rb") as fp:
        png = fp.read()

    # Capture information about user
    # host = request.META.get("HTTP_HOST", "")
    ip = request.META.get("REMOTE_ADDR", "")
    action = request.method
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    http_referrer = request.META.get("HTTP_REFERER", "")

    tracking_code_object = TrackingCode.objects.create(
        # url=request.path,
        # host=host,
        code=tracking_code,
        ip=ip,
        action=action,
        user_agent=user_agent,
        http_referrer=http_referrer,
    )

    if callback:
        callback(request, tracking_code, tracking_code_object)

    return HttpResponse(png, content_type="image/png")
