from django.conf import settings
import os

__author__ = 'nreed'

url_dict = {
    'validate': 'http://127.0.0.1:8000/om_validate/validate/',
    'scenarios': '/home/nreed/scenarios/',
    'openmalaria': getattr(settings, "PROJECT_ROOT", '') + '/om_validate/bin/'
}


def check_dir(local_dir):
    if os.name == "nt":
        if not local_dir.endswith('\\'):
            local_dir += '\\'
    else:
        if not local_dir.endswith('/'):
            local_dir += '/'

    return local_dir


def check_url(url, typ):
    if url is None or url == '':
        return url_dict[typ]

    if not url.endswith('/'):
        url += '/'

    return url
