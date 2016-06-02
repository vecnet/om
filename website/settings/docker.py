from .base import *

SECRET_KEY = get_env_variable("SECRET_KEY")

DEBUG = True

DATABASES = {
    'default':  {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'om',
        'USER': 'om',
        'PASSWORD': 'om',
        'HOST': 'db',
        'PORT': 5432,
    }
}

FILE_SERVER = {
    'URI schemes': ('data', 'file'), #, 'https'),
    'write scheme': 'data',
    'file scheme': {
        'root directory': '/tmp'
        # The path above is a real directory (the output directory for testing), so it'll pass validation.  This setting
        # should be set accordingly for each application environment.
    },
    # 'https scheme': {
    #     'root directory': '',
    #     # 'root directory': 'https://vecnet-qa.crc.nd.edu/webdav/qa/',
    #     'authentication': 'basic',
    #     'username': "webdav",
    #     'password': "webdav",
    #     # 'verify certificates': True,  # Optional; default = False
    # }
}

OPENMALARIA_EXEC_DIR = os.path.join(BASE_DIR, 'binaries/om/')
SIM_SERVICE_LOCAL_OM_EXECUTABLE = os.path.join(BASE_DIR, 'binaries/om/openMalaria')
TS_OM_SCENARIOS_DIR = os.path.join(BASE_DIR, 'scenarios')
