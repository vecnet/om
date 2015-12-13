# Copyright (C) 2015, University of Notre Dame
# All rights reserved
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from website.notification import set_notification as set_website_notification


class LoginRequiredMixin(object):
    """ This works: class InterviewListView(LoginRequiredMixin, ListView)
    This DOES NOT work: class InterviewListView(ListView, LoginRequiredMixin)
    I'm not 100% sure that wrapping as_view function using Mixin is a good idea though, but whatever
    """
    @classmethod
    def as_view(cls, **initkwargs):
        # Ignore PyCharm warning below, this is a Mixin class after all
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class NotificationMixin(object):
    SUCCESS = "alert-success"
    ERROR = "alert-danger"
    ALERT = "alert"
    INFO = "alert-info"

    def set_notification(self, message, alert_type=None):
        if alert_type is None:
            alert_type = NotificationMixin.INFO
        # Ignore PyCharm warning below, this is a Mixin class after all
        set_website_notification(self.request, message, alert_type)


class AjaxableResponseMixin(object):
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'xml': ""
            }
            return self.render_to_json_response(data)
        else:
            return response