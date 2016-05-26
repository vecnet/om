from .base import *


SECRET_KEY = get_env_variable("SECRET_KEY")

DATABASES = {
    'default': {
        'ENGINE': get_env_variable("DATABASE_ENGINE"),
        'NAME': get_env_variable("DATABASE_NAME"),
        'USER': get_env_variable("DATABASE_USER"),
        'PASSWORD': get_env_variable("DATABASE_PASSWORD"),
        'HOST': get_env_variable("DATABASE_HOST"),
        'PORT': get_env_variable("DATABASE_PORT"),
    }
}

EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

DEBUG = True

FILE_SERVER = {
    'URI schemes': ('data', 'file'), #, 'https'),
    'write scheme': 'data',
    'file scheme': {
        'root directory': '/tmp'
        # The path above is a real directory (the output directory for testing), so it'll pass validation.  This setting
        # should be set accordingly for each application environment.
    },
}

TS_OM_VALIDATE_URL = 'http://127.0.0.1:8000/validate/validate/'
