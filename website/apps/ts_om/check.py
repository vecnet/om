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

import os

from django.conf import settings

url_dict = {
    'validate': 'http://127.0.0.1:8000/om_validate/validate/',
    'scenarios': getattr(settings, "PROJECT_ROOT", '') + '/scenarios/',
    'openmalaria': getattr(settings, "PROJECT_ROOT", '') + '/om_validate/bin/'
}


def check_dir(local_dir, typ):
    if local_dir is None or local_dir == '':
        return url_dict[typ]

    if os.name == "nt":
        if not local_dir.endswith('\\'):
            local_dir += '\\'
    else:
        if not local_dir.endswith('/'):
            local_dir += '/'

    return local_dir


def check_url(url, typ):
    if url is None or url == '':
        return url_dict[typ]

    if not url.endswith('/'):
        url += '/'

    return url
