from django.contrib import admin
from django.core.urlresolvers import reverse
from .models import *

admin.site.register(DemographicsSnippet)
admin.site.register(BaselineScenario)
admin.site.register(Scenario)
admin.site.register(ModelSnippet)
admin.site.register(AnophelesSnippet)
admin.site.register(InterventionSnippet)
admin.site.register(InterventionComponent)


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
