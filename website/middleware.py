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

from django.http.response import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin


class HttpRedirectException(Exception):
    def __init__(self, url, message=""):
        super(self.__class__, self).__init__()
        self.message = message
        self.url = url


class RedirectionMiddleware(MiddlewareMixin):
    """ Redirect user if RedirectException is raised """
    @staticmethod
    def process_exception(request, exception):
        if isinstance(exception, HttpRedirectException):
            return HttpResponseRedirect(exception.url)
        return None
