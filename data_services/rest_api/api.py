"""
Versions of the REST API
"""

from tastypie.api import Api

from .resources import InputFileResource, OutputFileResource

v1_api = Api(api_name='v1')
v1_api.register(InputFileResource())
v1_api.register(OutputFileResource())
