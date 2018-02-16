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

from django.conf import settings


def get_site_url():
    """ Return URL of this website - i.e. http://127.0.0.1:8000 or https://om.vecnet.org """
    site_url = settings.SITE_URL
    if site_url[-1] == "/":
        site_url = site_url[:-1]
    return site_url
