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

from django.contrib.auth.models import User
from django.db import models


class PageVisit(models.Model):
    host = models.TextField()
    url = models.TextField()
    querystring = models.TextField()
    # GET, POST, etc
    action = models.TextField()
    http_code = models.TextField()
    http_referrer = models.TextField()
    user_agent = models.TextField()
    ip = models.TextField()
    # Auto saves on create
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    post_content = models.TextField(default="")

    def __unicode__(self):
        return "%s" % self.url


class TrackingCode(models.Model):
    code = models.TextField(blank=True)
    action = models.TextField(blank=True)
    http_referrer = models.TextField(blank=True)
    user_agent = models.TextField(blank=True)
    ip = models.TextField(blank=True)
    # Auto saves on create
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s" % self.code

    class Meta:
        get_latest_by = 'timestamp'
        managed = True  # Django manages the database table's lifecycle.
        ordering = ['timestamp', ]
