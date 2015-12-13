from django.http import HttpResponse
from data_services.models import Simulation
from django.core.exceptions import ObjectDoesNotExist


def download(request, simulation_id, name):
    simulation = Simulation.objects.get(id=simulation_id)
    print list(simulation.input_files.all())
    filename = name
    try:
        simulation_file = simulation.input_files.get(name=name)
        filename = simulation_file.metadata.get("filename", filename)
    except ObjectDoesNotExist:
        simulation_file = simulation.simulationoutputfile_set.get(name=name)

    response = HttpResponse(simulation_file.get_contents())
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response