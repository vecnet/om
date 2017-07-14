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
from django.contrib.admin import SimpleListFilter
from website.apps.big_brother.models import PageVisit, TrackingCode
from django.utils.translation import ugettext_lazy as _


class MacedFilter(SimpleListFilter):
    title = _("S.O.B.E.R items")
    parameter_name = "shoe_maced_items"

    def lookups(self, request, model_admin):
        return ("Yes", "Yes"), ("No", "No")

    def queryset(self, request, queryset):
        if self.value() == "Yes":
            return queryset.exclude(url__icontains="maced").exclude(url__icontains="/admin/")


class PageVisitAdmin(admin.ModelAdmin):
    list_display = ("url", "action", "user", "timestamp", "ip", "http_code")
    search_fields = ("url", "user__username", "user__first_name", "user__last_name")
    list_filter = ("user", MacedFilter, "http_code")

admin.site.register(PageVisit, PageVisitAdmin)


class TrackingCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "action", "timestamp", "ip", )
    search_fields = ("code", "ip")

admin.site.register(TrackingCode, TrackingCodeAdmin)
