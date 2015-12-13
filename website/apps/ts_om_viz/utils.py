from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from data_services.models import SimulationInputFile, SimulationOutputFile
from vecnet.openmalaria.output_parser import OutputParser


def om_output_parser_from_simulation(simulation):
    """

    :param simulation: data_services.models.Simulation object
    :return: vecnet.openmalaria.output_parser.OutputParser generated from simulation
    """
    sim_id = simulation.id

    # Get contents of xml input file and filename (if available)
    try:
        scenario_file = SimulationInputFile.objects.filter(simulations=simulation, name="scenario.xml")
        scenario = str(scenario_file[0].get_contents())
    except ObjectDoesNotExist:
        raise TypeError("No scenario.xml file in the simulation %s" % sim_id)
    except MultipleObjectsReturned:
        return TypeError("Multiple scenario.xml files are found in the simulation %s" % sim_id)

    # Get contents of survey output file
    try:
        output = SimulationOutputFile.objects.get(simulation=simulation, name="output.txt")
        output = output.get_contents()
    except ObjectDoesNotExist:
        output = None
    except MultipleObjectsReturned:
        raise TypeError("Multiple output.txt files in Simulation %s" % sim_id)

    # Get contents of continuous output file
    try:
        ctsout = SimulationOutputFile.objects.get(simulation=simulation, name="ctsout.txt")
        ctsout = ctsout.get_contents()
    except ObjectDoesNotExist:
        ctsout = None
    except MultipleObjectsReturned:
        raise TypeError("Multiple cstout.txt files in Simulation %s" % sim_id)

    if output is None and ctsout is None:
        raise TypeError("Error! Both output.txt and ctsout.txt are missing")

    oms = OutputParser(scenario, survey_output_file=output, cts_output_file=ctsout)
    return oms