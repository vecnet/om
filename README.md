[![Coverage Status](https://coveralls.io/repos/github/vecnet/om/badge.svg)](https://coveralls.io/github/vecnet/om)
[![Build Status](https://travis-ci.org/vecnet/om.svg?branch=master)](https://travis-ci.org/vecnet/om)

# Overview

OpenMalaria portal is a user-friendly web interface for OpenMalaria model. User can create
simulation, define environment and explore effect of interventions (drugs, spraying, bednets) on
malaria transmission levels. Model can be executed from the web interface using our
high-performance cluster.
Model output can be easily visualized or downloaded for further processing.


https://github.com/vecnet/om/assets/1641196/1965c836-0290-4f06-98a7-3414bf2a80fb


# System requirements

This Django project has been tested on Windows 8 x64, RedHat 7 and CentOS 7

* Django 1.11
* Python 3.5
* PostgreSQL 9.4
* Apache 2.4

# Quick Start Guide - Development

1. Create database structures
    `./manage.py migrate`

2. Create an admin user
   `./manage.py createsuperuser`

3. Run the server.
```bash
python manage.py runserver
```

# Using docker-compose.

```bash
docker-compose up
```


# Using Vagrant

1. Create Virtualbox VM `vagrant up`. It may take a while when starting VM for the first time

2. Login to VM using `vagrant ssh` command or your favorite ssh client. Login: vagrant, password vagrant

3. Switch to /vagrant directory `cd /vagrant`

4. Start django server `python manage.py runserver 0.0.0.0:8000`
Note you have to use 0.0.0.0 as server address, otherwise port forwarding may not work

You can edit files in your project directory, and changes will be visible to the virtual machine
(in /vagrant directory)

Credentials

*SSH* Login: vagrant, password vagrant

*PostgreSQL* Database: om, Login: om, Password: om

*Note*: To utilize the PostgreSQL database, create a `settings_local.py` file containing the following:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'om',
        'USER': 'om',
        'PASSWORD': 'om',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
```

# Configuration

1. By default, website.settings.dev is used for manage.py and website.settings.production is used in wsgi.py
It is typically required to change default settings file used in manage.py in production and qa environments

2. Create config_local.py in the root folder (next to wsgi.py and manage.py)

Note if DJANGO_SETTINGS_MODULE is defined, it takes precedence over settings_module in config_local.py

Example:
```python
settings_module = "website.settings.qa"
```
Check wsgi.py and manage.py to see how it works - they are different from default versions generated by Django.


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

# Enable VecNet SSO (VecNet instance only)

1. Install django-auth-pubtkt package
`pip install django-auth-pubtkt`

2. Copy public key for validating pubtkt tickets to /etc/httpd/conf/sso/tkt_pubkey_dsa.pem

# Let's encrypt it notes

```bash
/root/.acme.sh/acme.sh --issue -d om.vecnet.org -w /opt/portal/om.vecnet.org/apache/ --log
/root/.acme.sh/acme.sh --installcert -d om.vecnet.org --certpath /etc/httpd/ssl/om.vecnet.org.cer --keypath /etc/httpd/ssl/om.vecnet.org.key --fullchainpath /etc/httpd/ssl/om.vecnet.org.int.cer --reloadcmd "service httpd restart"
```
