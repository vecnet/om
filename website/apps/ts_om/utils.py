from django.core.files.base import ContentFile

from data_services.models import Simulation
from website.apps.ts_om.models import Scenario, Simulation


def migrate_simulations():
    for simulation in Simulation.objects.all():
        print simulation.id
        simulation_new = Simulation()
        input_file = simulation.input_files.filter(name="input.xml").first()
        if input_file:
            print input_file
            simulation_new.input_file.save(
                "scenario_%s.xml" % simulation_new.id,
                ContentFile(input_file.get_contents())
            )
        output_file = simulation.simulationoutputfile_set.filter(name="output.txt").first()
        if output_file:
            print output_file
            simulation_new.output_file.save(
                "output_%s.txt" % simulation_new.id,
                ContentFile(output_file.get_contents())
            )

        ctsout_file = simulation.simulationoutputfile_set.filter(name="ctsout.txt").first()
        if ctsout_file:
            print ctsout_file
            simulation_new.output_file.save(
                "ctsout_%s.txt" % simulation_new.id,
                ContentFile(ctsout_file.get_contents())
            )

        stdout = simulation.simulationoutputfile_set.filter(name="stdout.txt").first()
        if stdout:
            print stdout
            simulation_new.output_file.save(
                "stdout_%s.txt" % simulation_new.id,
                ContentFile(stdout.get_contents())
            )

        if simulation.status == "done":
            simulation_new.status = Simulation.COMPLETE
        elif simulation.status == "error":
            simulation_new.status = Simulation.FAILED
        elif simulation.status == "ready":
            simulation_new.status = Simulation.NEW

        simulation_new.save()
        scenario = simulation.scenario_set.all().first()
        if scenario:
            scenario.new_simulation = simulation_new
            scenario.save()
