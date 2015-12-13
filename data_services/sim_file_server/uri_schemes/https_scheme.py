from hashlib import md5
from io import BytesIO

import requests
import requests.auth

from .conf import ConfigurationError, SchemeConfiguration
from .handler_api import UriSchemeHandler
from .path_util import generate_relative_path
from data_services.errors import CallerError, DescriptionTemplate


class ConfigurationErrors:
    """
    Constants for configuration errors
    """
    DIRECTORY_NOT_STR = CallerError('"root directory" setting in https scheme settings is not a string')
    NO_DIRECTORY = CallerError('missing "root directory" setting in https scheme settings')
    NO_END_SLASH = CallerError('root directory must end with "/"')
    NO_PASSWORD = CallerError('missing "password" setting in https scheme settings')
    NO_USERNAME = CallerError('missing "username" setting in https scheme settings')
    NOT_DICT = CallerError('https scheme settings must be a dictionary')
    PASSWORD_NOT_STR = CallerError('"password" setting in https scheme settings is not a string')
    ROOT_DIR_NOT_EXIST = CallerError('the root directory does not exist')
    UNKNOWN_AUTH = CallerError(DescriptionTemplate('Unknown authentication method: $name'))
    USERNAME_NOT_STR = CallerError('"username" setting in https scheme settings is not a string')
    VERIFY_NOT_BOOL = CallerError('"verify certificates" setting is not a boolean')


class HttpsSchemeConfiguration(SchemeConfiguration):
    """
    Configuration of the https scheme handler.
    """

    #  The full path to the root directory where files are stored.
    root_directory = None

    #  Verify certificates in calls to requests library?
    verify_certificates = False

    #  Authentication callable for requests library - http://docs.python-requests.org/en/latest/user/authentication/
    authentication = None

    @classmethod
    def set_root_directory(cls, dir_url):
        """
        Set the root directory where files are stored on the WebDAV server.

        :param dir_url: full URL to root directory
        """
        if not dir_url or dir_url[-1] != '/':
            raise ConfigurationError(ConfigurationErrors.NO_END_SLASH)
        if not directory_exists(dir_url):
            raise ConfigurationError(ConfigurationErrors.ROOT_DIR_NOT_EXIST)
        cls.root_directory = dir_url

    def load_settings(self, settings):
        """
        Load the settings related to the file-scheme URLs.

        :param dict settings:  With the key "root directory"
        """
        if not isinstance(settings, dict):
            raise ConfigurationError(ConfigurationErrors.NOT_DICT)

        # 'root directory' setting
        try:
            directory = settings['root directory']
        except KeyError:
            raise ConfigurationError(ConfigurationErrors.NO_DIRECTORY)
        if not isinstance(directory, basestring):
            raise ConfigurationError(ConfigurationErrors.DIRECTORY_NOT_STR)

        # optional 'verify certificates' settings
        try:
            verify_certificates = settings['verify certificates']
            if not isinstance(verify_certificates, bool):
                raise ConfigurationError(ConfigurationErrors.VERIFY_NOT_BOOL)
            HttpsSchemeConfiguration.verify_certificates = verify_certificates
        except KeyError:
            pass

        auth = self.load_authentication_settings(settings)
        if auth:
            HttpsSchemeConfiguration.authentication = auth

        # Set directory after loading "verify certificates" and authentication settings because they are needed to
        # checked access to the root directory.
        self.set_root_directory(directory)

    @classmethod
    def load_authentication_settings(cls, settings):
        """
        Load optional authentication settings.  The 'authentication' key identifies the authentication method.  The
        particular method determines what additional settings are required:

            'authentication': 'basic',
            'username': '...',
            'password': '...',

        :param dict settings: Settings for the https scheme handler.
        :return: A callable that can be passed as the "auth" parameter to the requests library (see
                 http://docs.python-requests.org/en/latest/user/authentication/ for more details).  If there is no
                 authentication settings, None is returned.
        """
        try:
            authentication_method = settings['authentication']
        except KeyError:
            return None
        auth_methods = {
            'basic': cls.configure_basic_auth,
        }
        try:
            configure_auth = auth_methods[authentication_method]
        except KeyError:
            ConfigurationErrors.UNKNOWN_AUTH.description.placeholders['name'] = authentication_method
            raise ConfigurationError(ConfigurationErrors.UNKNOWN_AUTH)
        return configure_auth(settings)

    @classmethod
    def configure_basic_auth(cls, settings):
        """
        Load the configuration settings for basic HTTP authentication:

            'username': '...',
            'password': '...',

        :param dict settings: Settings for the https scheme handler.
        :return: A requests.auth.HTTPBasicAuth object.
        """
        try:
            username = settings['username']
        except KeyError:
            raise ConfigurationError(ConfigurationErrors.NO_USERNAME)
        if not isinstance(username, basestring):
            raise ConfigurationError(ConfigurationErrors.USERNAME_NOT_STR)
        try:
            password = settings['password']
        except KeyError:
            raise ConfigurationError(ConfigurationErrors.NO_PASSWORD)
        if not isinstance(password, basestring):
            raise ConfigurationError(ConfigurationErrors.PASSWORD_NOT_STR)
        return requests.auth.HTTPBasicAuth(username, password)

    @classmethod
    def as_kwargs(cls):
        """
        Get certain configuration settings formatted as keyword arguments that are passed to the requests library.
        """
        kwargs = dict(verify=cls.verify_certificates)
        if cls.authentication:
            kwargs['auth'] = cls.authentication
        return kwargs

    @classmethod
    def reset_settings(cls):
        """
        Reset all settings to their initial values.
        """
        cls.root_directory = None
        cls.verify_certificates = False
        cls.authentication = None


class HttpsSchemeHandler(UriSchemeHandler):
    """
    A handler that stores files on a WebDAV server using URLs with the "https:" scheme.
    """
    def __init__(self):
        assert HttpsSchemeConfiguration.root_directory is not None

    @property
    def scheme(self):
        return 'https'

    def store_file(self, contents):
        rel_path_components = generate_relative_path()
        subdirs = rel_path_components[:-1]
        file_name = rel_path_components[-1]

        # Walk down through subdirectories, making sure each one exists
        dir_url = HttpsSchemeConfiguration.root_directory
        for subdir in subdirs:
            dir_url += subdir + '/'
            if not directory_exists(dir_url):
                create_directory(dir_url)

        file_url = dir_url + file_name

        if isinstance(contents, str):
            md5_hash = write_data_to_file(contents, file_url)
        else:
            #  Assume contents is a file-like object
            file_obj = contents
            md5_hash = copy_data_to_file(file_obj, file_url)
        return file_url, md5_hash

    def open_in_read_mode(self, parsed_url):
        file_url = parsed_url.geturl()
        resp = requests.get(file_url, stream=True, **HttpsSchemeConfiguration.as_kwargs())
        assert resp.status_code == 200
        content_length = int(resp.headers['content-length'])
        IN_MEMORY_LIMIT = 100
        if content_length <= IN_MEMORY_LIMIT:
            #  Slurp all the contents into memory
            stream = BytesIO(resp.content)
            return stream
        else:
            return resp.raw


def directory_exists(dir_url):
    """
    Determine if a directory exists on the WebDAV server.

    :param string dir_url: Full URL to the directory on the server.
    """
    resp = requests.head(dir_url, **HttpsSchemeConfiguration.as_kwargs())
    return resp.status_code == 200


def create_directory(dir_url):
    """
    Create a directory on the WebDAV server.

    :param string dir_url: Full URL to the directory on the server.
    """
    resp = requests.Session().request("MKCOL", dir_url, **HttpsSchemeConfiguration.as_kwargs())
    assert resp.status_code == 201


def write_data_to_file(data, file_url):
    """
    Write data to a file on the WebDAV server.

    :param str data: Sequence of bytes to write.
    :param str file_url: Full URL to the file on the server.
    :return str: MD5 hash of the data that was written to the file.
    """
    resp = requests.put(file_url, data, **HttpsSchemeConfiguration.as_kwargs())
    assert resp.status_code == 201
    md5_hash = md5(data).hexdigest()
    return md5_hash


class Md5Reader(object):
    """
    Wraps a file-like object and calculates the MD5 hash of its contents as it's read.
    """

    def __init__(self, file_obj):
        self.file_obj = file_obj
        self.md5_hash = md5()

    def __iter__(self):
        CHUNK_SIZE = 4096
        while True:
            chunk = self.file_obj.read(CHUNK_SIZE)
            if not chunk:
                # EOF
                break
            self.md5_hash.update(chunk)
            yield chunk


def copy_data_to_file(file_obj, file_url):
    """
    Read the data (contents) from a file-like object and write the data to a local file.

    :param file_obj: The object to read the data from.
    :param str file_path: Full path to the local file.
    :return str: MD5 hash of the data that was written to the file.
    """
    file_reader = Md5Reader(file_obj)
    resp = requests.put(file_url, file_reader, **HttpsSchemeConfiguration.as_kwargs())
    assert resp.status_code == 201
    return file_reader.md5_hash.hexdigest()
