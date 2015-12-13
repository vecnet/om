# Copyright (C) 2015, University of Notre Dame
# All rights reserved

from .models import Simulation, SimulationOutputFile, SimulationInputFile, SimulationGroup
from django.contrib import admin

admin.site.register(SimulationGroup)
admin.site.register(Simulation)
admin.site.register(SimulationOutputFile)
admin.site.register(SimulationInputFile)
