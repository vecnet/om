from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from data_services.models import Simulation, SimulationGroup
from vecnet.simulation import sim_status
from sim_services import dispatcher
from website.apps.ts_om.submit import add_simulation
import time
import os


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.get(username="avyushko")
        sim_group = SimulationGroup(submitted_by_user=user)
        sim_group.save()
        print "Simulation group %s has been created successfully" % sim_group.id
        with open(os.path.join("ts_om","management", "commands", "default.xml")) as fp:
            xml = fp.read()
        simulation = add_simulation(sim_group, xml)
        print "Simulation %s has been created successfully" % simulation.id
        dispatcher.submit(sim_group)
        print "Simulation has been submitted successfully. Waiting for the results."
        seconds = 0
        print sim_status.SCRIPT_DONE
        while simulation.status != sim_status.SCRIPT_DONE and \
              simulation.status != sim_status.SCRIPT_ERROR and \
              simulation.status != sim_status.OUTPUT_ERROR:
            time.sleep(1)
            seconds += 1
            if divmod(seconds, 60):
                print "Waiting %s seconds, status %s" % (seconds, simulation.status)
            # reload model from the database
            simulation = Simulation.objects.get(id = simulation.id)
        print "Simulation result: %s" % simulation.status