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
