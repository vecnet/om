ALLOWED_HOSTS = [
    "127.0.0.1",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "om",
        "USER": "om",
        "PASSWORD": "om",
        "HOST": "127.0.0.1",
        "PORT": "",
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

SIM_SERVICE_LOCAL_OM_EXECUTABLE = "/opt/web/om/binaries/om/openMalaria"
TS_OM_VALIDATE_URL = 'http://127.0.0.1:80/validate/validate/'
PYTHON_EXECUTABLE = "/opt/venvs/om/bin/python"
