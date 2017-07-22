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


OPENMALARIA_EXEC_DIR = os.path.join(BASE_DIR, 'binaries/om/')
SIM_SERVICE_LOCAL_OM_EXECUTABLE = os.path.join(BASE_DIR, 'binaries/om/openMalaria')
TS_OM_SCENARIOS_DIR = os.path.join(BASE_DIR, 'scenarios')
