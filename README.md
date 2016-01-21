# Overview

This project is based on VecNet-CI - https://github.com/vecnet/vnetsource

#System requirements

This Django project has been tested on Windows 8 x64 and CentOS 7

#Quick Start Guide
1. Create database structures
    `./manage.py migrate`

2. Check if there are database migrations by reviewing the list of known migrations:
    `./manage.py migrate --list`

3. Create an admin user
   `./manage.py createsuperuser`

4. Load fixtures
```bash
python manage.py loaddata AnophelesSnippets
python manage.py loaddata BaselineScenarios
python manage.py loaddata DemographicsSnippets
python manage.py loaddata Interventions
```

#Database server configuration


#Using Vagrant

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

# Production deployment checklist

1. Change database to PostgreSQL in settings_local.py

2. Set DEBUG to False in settings_local.py

3. Generate new SECRET_KEY
 
4. Change ALLOWED_HOSTS and ADMINS accordingly

5. Set APP_ENV to 'production'

# Enable VecNet SSO

1. Install django-auth-pubtkt package
`pip install django-auth-pubtkt`

2. Copy public key for validating pubtkt tickets to /etc/httpd/conf/sso/tkt_pubkey_dsa.pem

3. Enable DjangoAuthPubtkt middleware
```MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django_auth_pubtkt.DjangoAuthPubtkt',
    'django.contrib.messages.middleware.MessageMiddleware',
) ```

4. Set configuration options below
```LOGIN_URL = "/sso/"
TKT_AUTH_LOGIN_URL = "https://www.vecnet.org/index.php/sso-login"
TKT_AUTH_PUBLIC_KEY = '/etc/httpd/conf/sso/tkt_pubkey_dsa.pem'
```


# TODOs
1. https://docs.djangoproject.com/en/1.6/ref/contrib/staticfiles/#django.contrib.staticfiles.storage.CachedStaticFilesStorage

Consider using static files storage to avoid caching issues

# Useful links
http://staticfiles.productiondjango.com/blog/stop-using-static-url-in-templates/
