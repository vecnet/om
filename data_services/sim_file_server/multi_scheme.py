from .api import FileServer
from .uri_schemes.data_scheme import DataSchemeHandler
from .uri_schemes.file_scheme import FileSchemeHandler
from .uri_schemes.https_scheme import HttpsSchemeHandler

handler_factories = {
    'data': DataSchemeHandler,
    'file': FileSchemeHandler,    # Cannot call constructor here because configuration settings may not be loaded yet
    'https': HttpsSchemeHandler,  # Cannot call constructor here because configuration settings may not be loaded yet
}


class MultiSchemeServer(FileServer):
    """
    A file server that handles multiple URI schemes.  It can open different schemes for reading, and it writes (stores)
    new files with one of the schemes.
    """

    @property
    def write_scheme(self):
        return self.handler_for_writing.scheme

    def __init__(self, read_schemes, write_scheme):
        """
        Initialize a new instance.

        :param read_schemes: Sequence of the URI schemes that the server will open for reading.
        :param write_scheme: The URI scheme that the server uses for writing (storing) new files.
        """
        self.handlers = dict()
        for scheme in read_schemes:
            self.handlers[scheme] = handler_factories[scheme]()
        if write_scheme not in read_schemes:
            raise ValueError('The scheme for writing files is not enabled for reading')
        self.handler_for_writing = handler_factories[write_scheme]()

    def store_file(self, contents):
        uri, md5_hash = self.handler_for_writing.store_file(contents)
        return uri, md5_hash

    def open_in_read_mode(self, parsed_url):
        try:
            handler = self.handlers[parsed_url.scheme]
        except KeyError:
            if parsed_url.scheme in handler_factories:
                scheme_status = 'Disabled'
            else:
                scheme_status = 'Unknown'
            raise ValueError('%s scheme in URI: %s' % (scheme_status, parsed_url.geturl()))
        return handler.open_in_read_mode(parsed_url)
