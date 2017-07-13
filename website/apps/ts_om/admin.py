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
import website.apps.ts_om.models as models

admin.site.register(models.DemographicsSnippet)
admin.site.register(models.BaselineScenario)

admin.site.register(models.ModelSnippet)
admin.site.register(models.AnophelesSnippet)
admin.site.register(models.InterventionSnippet)
admin.site.register(models.InterventionComponent)
admin.site.register(models.Simulation)


class ScenarioAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "status", "baseline", "deleted", "is_public", "last_modified",)
    list_filter = ("user", "new_simulation__status", "baseline", "deleted",)
    search_fields = ("id", "user__username", "description")

admin.site.register(models.Scenario, ScenarioAdmin)
