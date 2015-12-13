import json

from django.conf.urls import url
from django.core.files.base import ContentFile
from django.http import HttpResponse, StreamingHttpResponse
from tastypie import fields
from tastypie.exceptions import BadRequest, ImmediateHttpResponse
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from vecnet.simulation import sim_status

from .authorization import IpAddressBasedAuthorization
from ..models import Simulation, SimulationInputFile, SimulationOutputFile


class InputFileResource(ModelResource):
    class Meta:
        queryset = SimulationInputFile.objects.all()
        resource_name = 'input_files'
        excludes = ['uri']                # Since it currently has the file contents encoded in data: scheme
        detail_allowed_methods = ['get']
        list_allowed_methods = []
        authorization = IpAddressBasedAuthorization()

    def dehydrate_created_when(self, bundle):
        """
        Return the created_when field as UTC in ISO format 8601 format.  By default, this datetime field is being
        returned in the local timezone.
        """
        created_when = bundle.obj.created_when
        return created_when.isoformat()

    def dehydrate_metadata(self, bundle):
        """
        Return the metadata as a Python dictionary, so it'll be properly serialized.  If we don't convert it to a Python
        object, by default, the JSONField is serialized as a single string.
        """
        return dict(bundle.obj.metadata)

    # The two methods below are based on this SO answer:  http://stackoverflow.com/a/9454336/1258514
    # with these modifications:
    #   1) The code was updated to use prepend_urls (override_urls is deprecated).
    #   2) The download method in the answer uses FileWrapper which was introduced in Django 1.7, so I had to use
    #      ContentFile instead since we're using Django 1.5
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/download%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('download_file'),
                name="input_file_download"),
        ]

    def download_file(self, request, **kwargs):
        """
        Send a file through TastyPie without loading the whole file into memory at once.
        """
        if not IpAddressBasedAuthorization.is_authorized(request):
            return HttpResponse(status=401)

        input_file_django_obj = self._meta.queryset.get(pk=kwargs['pk'])
        file_contents = input_file_django_obj.get_contents()
        wrapped_content = ContentFile(file_contents)
        # TODO The use of ContentFile above causes this warning:
        #   .../virtualenvs/vecnet/lib/python2.7/site-packages/django/core/files/base.py:106:
        #       UnicodeWarning: Unicode equal comparison failed to convert both arguments to Unicode - interpreting them
        #       as being unequal
        #
        # The line in question isin the File.__iter__ method:
        #   if line[-1] in ('\n', '\r'):
        #
        # That line assumes the file contents are text, not binary.  This has been corrected in Django 1.7b1:
        #   https://github.com/django/django/commit/3841feee86cae65165f120db7a5d80ffc76dd520

        response = StreamingHttpResponse(wrapped_content, content_type='application/octet-stream')
        response['Content-Length'] = len(file_contents)
        return response


class OutputFileResource(ModelResource):

    class Meta:
        queryset = SimulationOutputFile.objects.all()
        resource_name = 'output-files'
        list_allowed_methods = ['post']
        detail_allowed_methods = []
        authorization = IpAddressBasedAuthorization()

    class Errors:
        """
        Errors that can occur with this resource.
        """
        FILES_NOT_OBJECT = 'The value for output_files is not a JSON object'
        INVALID_ID = 'Invalid value for id_on_client'
        INVALID_JSON = 'Invalid JSON in request body'
        LINE_NOT_STRING = 'Line in file contents is not a string'
        NO_ID_ON_CLIENT = 'Missing "id_on_client" name in JSON object'
        NO_OUTPUT_FILES = 'Missing "output_files" name in JSON object'
        NOT_JSON_OBJECT = 'Request body is not a JSON object'
        NOT_STR_OR_ARRAY = 'File contents is not a string or array of strings'
        UNKNOWN_NAMES = '1 or more unknown names for output files'

    def make_error_response(self, request, error, error_details=None, simulation=None):
        error_info = {
            'error': error,
        }
        if error_details is not None:
            error_info['error_details'] = str(error_details)
        if simulation is not None:
            update_status(simulation, sim_status.OUTPUT_ERROR)
        return ImmediateHttpResponse(self.error_response(request, error_info))

    def post_list(self, request, **kwargs):
        """
        Expected payload:
            {
                "id_on_client" : "string (pk of simulation)",
                "output_files" :
                {
                    "filename 1" : "contents...",
                    "filename 2" : "contents...",
                }
            }
        """
        try:
            payload = self.deserialize(request, request.body)
        except BadRequest:
            raise self.make_error_response(request, self.Errors.INVALID_JSON)
        if not isinstance(payload, dict):
            raise self.make_error_response(request, self.Errors.NOT_JSON_OBJECT,
                                           'Expected dictionary but got %s instead' % type(payload))

        # Get the specified simulation
        if 'id_on_client' not in payload:
            raise self.make_error_response(request, self.Errors.NO_ID_ON_CLIENT)
        try:
            id_on_client = int(payload['id_on_client'])
        except ValueError:
            raise self.make_error_response(request, self.Errors.INVALID_ID)
        try:
            simulation = Simulation.objects.get(pk=id_on_client)
        except Simulation.DoesNotExist:
            raise self.make_error_response(request, self.Errors.INVALID_ID)

        # Check the list of output file names
        update_status(simulation, sim_status.STAGING_OUTPUT)
        if 'output_files' not in payload:
            raise self.make_error_response(request, self.Errors.NO_OUTPUT_FILES,
                                           simulation=simulation)
        output_files = payload['output_files']
        if not isinstance(output_files, dict):
            raise self.make_error_response(request, self.Errors.FILES_NOT_OBJECT,
                                           simulation=simulation)
        valid_names = get_output_file_names(simulation)
        unknown_names = filter(lambda x: x not in valid_names, output_files.keys())
        if unknown_names:
            raise self.make_error_response(request, self.Errors.UNKNOWN_NAMES,
                                           'Unknown names: ' + ', '.join(unknown_names),
                                           simulation=simulation)

        # Store the output files
        for name, contents in output_files.iteritems():
            if isinstance(contents, list):
                for index, line in enumerate(contents):
                    if not isinstance(line, basestring):
                        raise self.make_error_response(request, self.Errors.LINE_NOT_STRING,
                                                       'Array item [%d] = %s' % (index, repr(line)),
                                                       simulation=simulation)
                contents = ''.join(contents)
            elif not isinstance(contents, basestring):
                raise self.make_error_response(request, self.Errors.NOT_STR_OR_ARRAY,
                                               'contents type = %s' % type(contents),
                                               simulation=simulation)
            sim_output_file = SimulationOutputFile.objects.create_file(contents, name=name, simulation=simulation)
        update_status(simulation, sim_status.SCRIPT_DONE)


def update_status(simulation, new_status):
    """
    Update a simulation's status.
    """
    assert isinstance(simulation, Simulation)
    simulation.status = new_status
    simulation.save()


def get_output_file_names(simulation):
    """
    Get the list of names for a simulation's output files.  The list may be fixed for a particular simulation model
    (for example, OpenMalaria).  The list may depend upon the information in the simulation's input files (if an input
    file contains the name of another input file).
    """
    # For now, we assume it's an OpenMalaria or EMOD simulation
    # TODO: use the simulation's model field
    return ('model_stdout_stderr.txt',
            'ctsout.txt', 'output.txt',
            'BinnedReport.json', 'DemographicsSummary.json', 'InsetChart.json', 'VectorSpeciesReport.json')