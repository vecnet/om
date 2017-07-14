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

from django.contrib import admin
from website.apps.email.models import DoNotSendEmailList, Email


class DoNotSendEmailListAdmin(admin.ModelAdmin):
    list_display = ("email", "notes", "creation_timestamp", "last_modified_timestamp")
    list_filter = ("email", "notes")


admin.site.register(DoNotSendEmailList, DoNotSendEmailListAdmin)


class EmailAdmin(admin.ModelAdmin):
    search_fields = ("email_recipient", "from_address", "email_subject", "status")
    list_display = ("email_recipient", "from_address", "email_subject",  "status", # "tracking_code",
                    "last_error_message",
                    "sent_timestamp", )
    list_filter = ("status",)
    ordering = ("-creation_timestamp", )

admin.site.register(Email, EmailAdmin)
