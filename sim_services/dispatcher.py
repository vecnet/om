"""
Prototype of functionality that will eventually reside in Simulation Services (Job Services v3).
This code is independent of the simulation model being executed.
"""

import json
import re

from django.conf import settings
from django.utils import timezone
import requests
from vecnet.simulation import ExecutionRequest, sim_model, Simulation, SimulationGroup

from data_services import models as data_models
from data_services.rest_api.api import InputFileResource, OutputFileResource  #  Imported from the api module instead of
                                            #  resources module to ensure proper API initialization.
                                            # See https://groups.google.com/forum/#!topic/django-tastypie/VZoFaBossnw


class RestApiMeta(type):
    """
    Metaclass for REST API class below.
    """
    _site_root_url_no_trailing_slash = None
    _input_files_endpoint = None
    _output_files_endpoint = None

    @property
    def site_root_url_no_trailing_slash(self):
        """
        The absolute URL to the site's root, without the trailing slash (i.e., "scheme://host[:port]")
        """
        if self._site_root_url_no_trailing_slash is None:
            self._site_root_url_no_trailing_slash = re.sub(r'/$', '', settings.SITE_ROOT_URL)
        return self._site_root_url_no_trailing_slash

    @property
    def output_files_endpoint(self):
        """
        The absolute URL for the endpoint of output file resources
        """
        if self._output_files_endpoint is None:
            self._output_files_endpoint = self.site_root_url_no_trailing_slash + OutputFileResource().get_resource_uri()
        return self._output_files_endpoint


class RestApi(object):
    """
    Helper properties for REST API endpoints
    """
    __metaclass__ = RestApiMeta

    @classmethod
    def get_download_url(cls, input_file):
        """
        Get the absolute URL for downloading a simulation input file.
        """
        assert isinstance(input_file, data_models.SimulationInputFile)
        absolute_file_url = cls.site_root_url_no_trailing_slash + InputFileResource().get_resource_uri(input_file)
        download_url = absolute_file_url + 'download/'
        return download_url


def create_sim_resource_repr(simulation):
    """
    Create a REST resource representation for a simulation.
    """
    assert isinstance(simulation, data_models.Simulation)
    simulation_resource_repr = Simulation(model=simulation.model,
                                          model_version=simulation.version,
                                          id_on_client=str(simulation.id),
                                          output_url=RestApi.output_files_endpoint)
    for input_file in simulation.input_files.all():
        input_file_uri = RestApi.get_download_url(input_file)
        simulation_resource_repr.input_files[input_file.name] = input_file_uri  # TODO: eventually use input_file.uri
    return simulation_resource_repr


def create_group_resource_repr(sim_group):
    """
    Create a REST resource representation for a simulation group
    """
    assert isinstance(sim_group, data_models.SimulationGroup)
    group_resource_repr = SimulationGroup()
    for simulation in sim_group.simulations.all():
        group_resource_repr.simulations.append(create_sim_resource_repr(simulation))
    return group_resource_repr


def submit(simulation_group):
    """
    Submit a simulation group to the default cluster for execution.
    Raises RuntimeError if the submission fails for some reason.
    """
    assert isinstance(simulation_group, data_models.SimulationGroup)

    simulation_group_resource_repr = create_group_resource_repr(simulation_group)
    execution_request = ExecutionRequest(simulation_group=simulation_group_resource_repr)
    execution_request_string = json.dumps(execution_request.to_dict())

    headers = {
        'Authorization': "ApiKey %s:%s" % (settings.SIMULATION_MANAGER_API_USER,
                                           settings.SIMULATION_MANAGER_API_KEY),
        'Content-type': "application/json",
    }

    simulation_group.submitted_when = timezone.now()
    simulation_group.save()

    post_request = requests.post(settings.SIMULATION_MANAGER_URL, execution_request_string, headers=headers)
    print post_request.status_code

    if post_request.status_code == 201:
        # TODO: store the URL in response's Location header; Need this URL to get sim group's status
        pass
    else:
        raise RuntimeError(post_request.text)