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
from django.core.urlresolvers import reverse
from .models import *

admin.site.register(DemographicsSnippet)
admin.site.register(BaselineScenario)

admin.site.register(ModelSnippet)
admin.site.register(AnophelesSnippet)
admin.site.register(InterventionSnippet)
admin.site.register(InterventionComponent)
admin.site.register(Simulation)


class ExperimentFileAdmin(admin.ModelAdmin):
    def test_simulation_group(self, experiment):
        if experiment.test_sim_group:
            return "<a href='%s'>%s</a>" % (reverse("admin:data_services_simulationgroup_change",
                                                    args=(experiment.test_sim_group.id,)),
                                            experiment.test_sim_group.id,)

    test_simulation_group.allow_tags = True

    def simulation_group(self, experiment):
        if experiment.sim_group:
            return "<a href='%s'>%s</a>" % (reverse("admin:data_services_simulationgroup_change",
                                                    args=(experiment.sim_group.id,)), experiment.sim_group.id,)

    simulation_group.allow_tags = True

    list_display = ("id", "name", "file", "test_simulation_group", "simulation_group",)
    list_filter = ("user",)
    search_fields = ("id", "name", "test_sim_group__id", "sim_group__id")


admin.site.register(ExperimentFile, ExperimentFileAdmin)

class ScenarioAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "status", "baseline", "deleted", "is_public", "last_modified",)
    list_filter = ("user", "new_simulation__status", "baseline", "deleted",)
    search_fields = ("id", "user__username", "description")

admin.site.register(Scenario, ScenarioAdmin)
