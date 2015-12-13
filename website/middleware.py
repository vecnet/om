# Copyright (C) 2015, University of Notre Dame
# All rights reserved
from django.http.response import HttpResponseRedirect


class HttpRedirectException(Exception):
    def __init__(self, url, message=""):
        super(self.__class__, self).__init__()
        self.message = message
        self.url = url


class RedirectionMiddleware(object):
    """ Redirect user if RedirectException is raised """
    @staticmethod
    def process_exception(request, exception):
        if isinstance(exception, HttpRedirectException):
            return HttpResponseRedirect(exception.url)
        return None
