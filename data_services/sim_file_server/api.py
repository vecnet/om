from abc import ABCMeta, abstractmethod, abstractproperty

from .util import custom_urlparse


class FileServer(object):
    """
    API to a file server.
    """
    __metaclass__ = ABCMeta

    @abstractproperty
    def write_scheme(self):
        """
        Get the URL scheme that the server uses to store new files.

        :rtype: str
        """
        raise NotImplementedError

    @abstractmethod
    def store_file(self, contents):
        """
        Store a new file on the server.

        :param contents: The file's actual contents if a str.  Otherwise, it's a file-like object from which the
                         contents can be read.
        :type  contents: str or file-like object

        :returns: A tuple with: URI of the file on the server, and its MD5 hash (string of hexadecimal digits)
        """
        raise NotImplementedError

    def open_for_reading(self, uri):
        """
        Open a file on the server for reading.

        :param str uri: The file's URI.

        :returns file-like: A file-like object with at least read() method for reading the file's contents in binary
                            mode.  The object is a context manager so it can be used in a "with" statement.
        """
        parsed_url = custom_urlparse(uri)
        if parsed_url.scheme == '':
            raise ValueError('No scheme in URI: %s', uri)
        return self.open_in_read_mode(parsed_url)

    @abstractmethod
    def open_in_read_mode(self, parsed_url):
        """
        Open a file in read mode.

        :param parsed_url: The file's URL.
        :type  parsed_url: urlparse.ParseResult

        :returns file-like: A file-like object with at least read() method for reading the file's contents in binary
                            mode.  The object is a context manager so it can be used in a "with" statement.
        """
        raise NotImplementedError
