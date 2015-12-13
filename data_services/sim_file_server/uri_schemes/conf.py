from abc import ABCMeta, abstractmethod


class SchemeConfiguration(object):
    """
    API for configuring the handler for a particular URI scheme.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def load_settings(self, settings):
        """
        Load the scheme's settings.

        :param object settings: The expected type depends upon the particular scheme.

        :raises: An django.conf.ImproperlyConfigured object with an error code as args[0]
        """
        raise NotImplementedError

    @abstractmethod
    def reset_settings(self):
        """
        Reset all the scheme's settings to their default values.
        """
        raise NotImplementedError


class ConfigurationError(Exception):
    """
    Represents a configuration error
    """
    pass
