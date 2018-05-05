from .base import *


SECRET_KEY = "lskfjaldfisdofjadfidsfsdf"

DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql_psycopg2",
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

SITE_URL = "http://localhost:8083"
