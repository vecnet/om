from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from data_services.models import Simulation
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied


@login_required
def download_view(request, simulation_id, name):
    simulation = Simulation.objects.get(id=simulation_id)
    if simulation.scenario_set.count() > 0:
        scenario = simulation.scenario_set.all()[0]
        if scenario.user != request.user:
            raise PermissionDenied

    filename = name
    try:
        simulation_file = simulation.input_files.get(name=name)
        filename = simulation_file.metadata.get("filename", filename)
    except ObjectDoesNotExist:
        simulation_file = simulation.simulationoutputfile_set.get(name=name)

    response = HttpResponse(simulation_file.get_contents())
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response