import os

from django.conf import settings

__author__ = 'nreed'

url_dict = {
    'validate': 'http://127.0.0.1:8000/om_validate/validate/',
    'scenarios': getattr(settings, "PROJECT_ROOT", '') + '/scenarios/',
    'openmalaria': getattr(settings, "PROJECT_ROOT", '') + '/om_validate/bin/'
}


def check_dir(local_dir, typ):
    if local_dir is None or local_dir == '':
        return url_dict[typ]

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
