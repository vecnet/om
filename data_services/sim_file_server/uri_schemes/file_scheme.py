from hashlib import md5
import os

from .conf import ConfigurationError, SchemeConfiguration
from .handler_api import UriSchemeHandler
from .path_util import generate_relative_path
from data_services.errors import CallerError


class ConfigurationErrors:
    """
    Constants for configuration errors
    """
    DIRECTORY_NOT_STR = CallerError('"root directory" setting in file scheme settings is not a string')
    NO_DIRECTORY = CallerError('missing "root directory" setting in file scheme settings')
    NOT_DICT = CallerError('file scheme settings must be a dictionary')
    ROOT_DIR_NOT_EXIST = CallerError('the root directory does not exist')
    ROOT_NOT_DIR = CallerError('path is not a directory')


class FileSchemeConfiguration(SchemeConfiguration):
    """
    Configuration of the file scheme handler.
    """

    #  The full path to the root directory where files are stored.
    root_directory = None

    @classmethod
    def set_root_directory(cls, dir_path):
        """
        Set the root directory where files are stored on the local file system.

        :param dir_path: full path to root directory
        """
        if os.path.isdir(dir_path):
            cls.root_directory = dir_path
        else:
            if not os.path.exists(dir_path):
                raise ConfigurationError(ConfigurationErrors.ROOT_DIR_NOT_EXIST)
            else:
                raise ConfigurationError(ConfigurationErrors.ROOT_NOT_DIR)

    def load_settings(self, settings):
        """
        Load the settings related to the file-scheme URLs.

        :param dict settings:  With the key "directory"
        """
        if not isinstance(settings, dict):
            raise ConfigurationError(ConfigurationErrors.NOT_DICT)
        try:
            directory = settings['root directory']
        except KeyError:
            raise ConfigurationError(ConfigurationErrors.NO_DIRECTORY)
        if not isinstance(directory, basestring):
            raise ConfigurationError(ConfigurationErrors.DIRECTORY_NOT_STR)
        self.set_root_directory(directory)

    @classmethod
    def reset_settings(cls):
        """
        Reset all settings to their initial values.
        """
        cls.root_directory = None


class FileSchemeHandler(UriSchemeHandler):
    """
    A handler that stores files on the local file system, so its uses URLs with the "file:" scheme.
    """
    def __init__(self):
        assert FileSchemeConfiguration.root_directory is not None

    @property
    def scheme(self):
        return 'file'

    def store_file(self, contents):
        rel_path_components = generate_relative_path()
        rel_path = os.path.join(*rel_path_components)
        file_path = os.path.join(FileSchemeConfiguration.root_directory, rel_path)
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        if isinstance(contents, str):
            md5_hash = write_data_to_file(contents, file_path)
        else:
            #  Assume contents is a file-like object
            file_obj = contents
            md5_hash = copy_data_to_file(file_obj, file_path)
        uri = 'file:///' + rel_path
        return uri, md5_hash

    def open_in_read_mode(self, parsed_url):
        # urlparse library leaves the "/" that separates netloc from path on the front of the path
        rel_path = parsed_url.path.lstrip('/')
        file_path = os.path.join(FileSchemeConfiguration.root_directory, rel_path)
        if not os.path.exists(file_path):
            raise ValueError('URI does not exist: %s' % parsed_url.get_url())
        if not os.path.isfile(file_path):
            raise ValueError('URI is not a file: %s' % parsed_url.get_url())
        return open(file_path, 'rb')


def write_data_to_file(data, file_path):
    """
    Write data to a local file.

    :param str data: Sequence of bytes to write.
    :param str file_path: Full path to the local file.
    :return str: MD5 hash of the data that was written to the file.
    """
    with open(file_path, 'wb') as f:
        f.write(data)
    md5_hash = md5(data).hexdigest()
    return md5_hash


def copy_data_to_file(file_obj, file_path):
    """
    Read the data (contents) from a file-like object and write the data to a local file.

    :param file_obj: The object to read the data from.
    :param str file_path: Full path to the local file.
    :return str: MD5 hash of the data that was written to the file.
    """
    md5_hash = md5()
    CHUNK_SIZE = 4096
    with open(file_path, 'wb') as f:
        while True:
            chunk = file_obj.read(CHUNK_SIZE)
            if not chunk:
                # EOF
                break
            f.write(chunk)
            md5_hash.update(chunk)
    return md5_hash.hexdigest()
