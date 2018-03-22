# Overview

OpenMalaria portal is a user-friendly web interface for OpenMalaria model. User can create
simulation, define environment and explore effect of interventions (drugs, spraying, bednets) on
malaria transmission levels. Model can be executed from the web interface using our
high-performance cluster.
Model output can be easily visualized or downloaded for further processing.

# System requirements

* Django 1.11
* Python 3.5
* PostgreSQL 9.4
* Apache 2.4
* RedHat 7 or CentOS 7


# Deployment instruction

1. Install apache, postgresql, python 3.5 and mod_wsgi 3.5, system libraries

You can use install_centos.sh script to install most of dependencies

2. Clone repository into /opt/portal/om.vecnet.org

```bash
git clone https://github.com/vecnet/om /opt/portal/om.vecnet.org
```

3. Create settings_local.py in website/settings directory. Example:

```python
DEBUG = False
SECRET_KEY = 'z5azf=qbb%lmzd^xf9#g5bqtv30e%12P!t(&!0hkpzp0jc8q5$'
DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql_psycopg2",
        'NAME': "om",
        'USER': "om",
        'PASSWORD': "om",
        'HOST': "127.0.0.1",
        'PORT': "5432",
    }
}
ADMINS = [
    ('Alex', 'avyushko@nd.edu'),
]

ALLOWED_HOSTS = [
    'om.vecnet.org',
]
```

4. Setup cron jobs:
`python manage.py crontab add`

5. Create database structures. Note that your database user must have "CREATE TABLE" permission
    `./manage.py migrate`

3. Create an admin user
   `./manage.py createsuperuser`

# Enable VecNet SSO (VecNet instance only)

1. Install django-auth-pubtkt package
`pip install django-auth-pubtkt`

2. Copy public key for validating pubtkt tickets to /etc/httpd/conf/sso/tkt_pubkey_dsa.pem
