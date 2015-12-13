from datetime import datetime
from uuid import uuid4


def generate_relative_path():
    """
    Generate a new relative path that will be used from a scheme handler's root directory.

    :return: Tuple of components in the relative path from the root directory to a new file (one that doesn't exist
             yet).
    """
    # Use the current date and time so there's some order to the files which will make it easier for humans to
    # navigate among the files.
    now = datetime.now()
    now_date = now.strftime('%Y-%m-%d')             # e.g., '2011-02-14'
    now_hhmm = now.strftime('%Hh_%I%M%p').lower()   # e.g., '00h_1209am', '18h_0622pm'
    now_secs = now.strftime('%S.%f')                # e.g., '58.012345'

    # Also incorporate a random UUID to ensure that the path is unique.  Pack it down to fewer portable-filename
    # characters based on this SO answer:  http://stackoverflow.com/a/12270917
    uuid_packed = uuid4().bytes.encode('base64').rstrip('=\n').replace('/', '_').replace('+', '-')

    return now_date, now_hhmm, '{}_{}'.format(now_secs, uuid_packed)
