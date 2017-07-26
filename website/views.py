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
logger = logging.getLogger(__name__)

from website.notification import set_notification


# Keep this view for testing purposes
def test_http_code_500(request):
    # View to test
    # - HTTP 500 handler in production mode (when DEBUG = False)
    # - Django logging configuration
    set_notification(request, "hello", "alert-info")
    logger.debug("Raising RuntimeError - just because")
    raise RuntimeError
