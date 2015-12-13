from django.conf import settings
from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized


class IpAddressBasedAuthorization(Authorization):
    """
    Authorization based on the client's IP address.

    Only clients whose address is in the DATA_REST_API_CLIENTS setting are authorized.
    """

    @classmethod
    def is_authorized(cls, request):
        client_ip_addr = request.META.get('REMOTE_ADDR')
        return client_ip_addr in settings.DATA_REST_API_CLIENTS

    def read_detail(self, object_list, bundle):
        if not self.is_authorized(bundle.request):
            raise Unauthorized
        return True

    # ---------------------------------------
    # All other operations are not authorized

    def read_list(self, object_list, bundle):
        raise Unauthorized

    def create_list(self, object_list, bundle):
        raise Unauthorized

    def create_detail(self, object_list, bundle):
        raise Unauthorized

    def update_list(self, object_list, bundle):
        raise Unauthorized

    def update_detail(self, object_list, bundle):
        raise Unauthorized

    def delete_list(self, object_list, bundle):
        raise Unauthorized

    def delete_detail(self, object_list, bundle):
        raise Unauthorized
