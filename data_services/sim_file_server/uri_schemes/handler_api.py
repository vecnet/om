from abc import ABCMeta, abstractmethod, abstractproperty


class UriSchemeHandler(object):
    """
    API to a URI scheme handler.
    """
    __metaclass__ = ABCMeta

    @abstractproperty
    def scheme(self):
        """
        Get the URL scheme that the handler understands.

        :rtype: str
        """
        raise NotImplementedError

    @abstractmethod
    def store_file(self, contents):
        """
        Store a new file.

        :param contents: The file's actual contents if a str.  Otherwise, it's a file-like object from which the
                         contents can be read.
        :type  contents: str or file-like object

        :returns: A tuple with: URI of the file, and its MD5 hash (string of hexadecimal digits)
        """
        raise NotImplementedError

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
