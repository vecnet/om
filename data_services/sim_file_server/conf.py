from data_services.errors import CallerError, DescriptionTemplate

from .multi_scheme import MultiSchemeServer
from .uri_schemes.conf import ConfigurationError
from .uri_schemes.file_scheme import FileSchemeConfiguration
from .uri_schemes.https_scheme import HttpsSchemeConfiguration

# Factory function that returns the active file server (think of it as a connection to the server)
_server_factory = None


def get_active_server():
    """
    Get the active file server.
    """
    global _server_factory
    if _server_factory is None:
        _server_factory = read_configuration()
    active_server = _server_factory()
    return active_server


class Errors:
    """
    Constants that represent different types of configuration errors.
    """
    NO_FILE_SCHEME_SETTINGS = CallerError('no "file scheme" settings in FILE_SERVER')
    NO_HTTPS_SCHEME_SETTINGS = CallerError('no "https scheme" settings in FILE_SERVER')
    NO_URI_SCHEMES = CallerError('no "URI schemes" setting in FILE_SERVER')
    NO_WRITE_SCHEME = CallerError('no "write scheme" setting in FILE_SERVER')
    UNKNOWN_SCHEME = CallerError(DescriptionTemplate('Unknown scheme ($name) in "URI schemes" setting in FILE_SERVER'))


SCHEME_CONFIGURATIONS = {
    'data': (None, None),
    'file': (FileSchemeConfiguration(), Errors.NO_FILE_SCHEME_SETTINGS),
    'https': (HttpsSchemeConfiguration(), Errors.NO_HTTPS_SCHEME_SETTINGS),
}


def read_configuration():
    """
    Read the Django settings related to the file server.

    :return: Factory function that returns the file server specified in the settings.
    """
    # To avoid circular import problems, import Django settings when this function is called rather than when this
    # module is imported.
    from django.conf import settings

    read_schemes, write_scheme = get_uri_schemes(settings.FILE_SERVER)
    server_factory = lambda : MultiSchemeServer(read_schemes, write_scheme)
    return server_factory


def get_uri_schemes(server_settings):
    """
    Get the URI schemes that the server is configured to read and which scheme it uses to store new files.

    :param dict server_settings:  Settings for the file server
    :return: A tuple: sequence of URI schemes (strings) for reading, string with URI scheme for writing
    """
    assert isinstance(server_settings, dict)
    try:
        read_schemes = server_settings['URI schemes']
    except KeyError:
        raise improperly_configured(Errors.NO_URI_SCHEMES)
    for scheme in read_schemes:
        try:
            scheme_configuration, no_scheme_settings_error = SCHEME_CONFIGURATIONS[scheme]
        except KeyError:
            Errors.UNKNOWN_SCHEME.description.placeholders['name'] = scheme
            raise improperly_configured(Errors.UNKNOWN_SCHEME)
        if scheme_configuration:
            try:
                scheme_configuration.load_settings(server_settings[scheme + ' scheme'])
            except KeyError:
                raise improperly_configured(no_scheme_settings_error)
            except ConfigurationError, exc:
                raise improperly_configured(exc.args[0])

    try:
        write_scheme = server_settings['write scheme']
    except KeyError:
        raise improperly_configured(Errors.NO_WRITE_SCHEME)
    return read_schemes, write_scheme


def improperly_configured(arg0):
    """
    Create a new instance of the ImproperlyConfigured exception.  This helper function exists so every caller function
    doesn't have to import the exception class.

    :param arg0: Identifier for the particular configuration error.
    :return: An ImproperlyConfigured object.
    """
    from django.conf import ImproperlyConfigured
    return ImproperlyConfigured(arg0)


class TestingAPI:
    """
    API for unit tests of this module.
    """

    @staticmethod
    def reset_configuration():
        """
        Reset all configuration settings to their initial default values.
        """
        global _server_factory
        _server_factory = None
        for scheme_configuration, _ in SCHEME_CONFIGURATIONS.itervalues():
            if scheme_configuration:
                scheme_configuration.reset_settings()
