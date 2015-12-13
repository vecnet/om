from hashlib import md5
from io import BytesIO
import urllib

from .handler_api import UriSchemeHandler

# Internet media type for "data" scheme URIs because they may contain text or binary data
MEDIA_TYPE = 'application/octet-stream'

# The characters at the start of every URI
PATH_PREFIX = MEDIA_TYPE + ','


class DataSchemeHandler(UriSchemeHandler):
    """
    A scheme handler that stores a file's contents in its URL using the "data:" scheme.
    """

    @property
    def scheme(self):
        return 'data'

    def store_file(self, contents):
        if not isinstance(contents, basestring):
            #  Read contents from file-like object
            contents = contents.read()
        # Encode unsafe characters (ASCII characters with special meanings in URLs, i.e., "reserved characters", along
        # with unprintable characters, 0x00 to 0x15 (0 to 31 decimal) and 0x7F to 0xFF (127 to 255 decimal).
        contents_quoted = urllib.quote(contents,
                                       safe='')  # Override default value of "safe" arg ('/') so slashes encoded too
        uri = '{}:{}{}'.format(self.scheme, PATH_PREFIX, contents_quoted)
        md5_hash = md5(contents).hexdigest()
        return uri, md5_hash

    def open_in_read_mode(self, parsed_url):
        if parsed_url.path.startswith(PATH_PREFIX):
            contents_quoted = parsed_url.path[len(PATH_PREFIX):]
            try:
                contents = urllib.unquote(str(contents_quoted))
            except UnicodeEncodeError:
                raise ValueError("URI path contains unicode characters")
        elif parsed_url.path.startswith(','):
            # Existing unsafe URLs that haven't been migrated yet
            contents = parsed_url.path[1:]
        else:
            raise ValueError('URI path does not start with "{}": {}'.format(PATH_PREFIX, parsed_url.geturl()))
        if isinstance(contents, unicode):
            # In Python 2.x, convert to bytes
            contents = contents.encode('utf-8')
        #  Use io library since its classes all derive from IOBase which is a context manager (and hence, can be used
        #  in "with" statements).
        stream = BytesIO(contents)
        return stream