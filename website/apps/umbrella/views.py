# Copyright (C) 2015, University of Notre Dame
# All rights reserved
import json
import os
from django.http import HttpResponse

FILES_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_umbrella_specification_view(request, *args, **kwargs):
    # Using json template to generate Umbrella specification
    umbrella_spec = json.load(open(os.path.join(FILES_DIR, "files", "openmalaria.umbrella")))
    # umbrella_spec["data"]["scenario.xml"]["source"] = ["http://localhost:8000/ts_om/%s/download" % kwargs["scenario_id"]]
    return HttpResponse(content=json.dumps(umbrella_spec), content_type="application/json")