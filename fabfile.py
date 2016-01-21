# This file is part of the OpenMalaria Basic Usert Interface project.
#
# For copyright and licensing information about this package, see the
# NOTICE.txt and LICENSE.txt files in its top-level directory; they are
# available at https://github.com/vecnet/om
#

from fabric.api import local, sudo

def update():
    # local("sudo chown -R $USER:apache website/media")
    # local("chmod 775 -R website/media")
    local('git pull')
    local('pip install -r requirements.txt')
    local('python manage.py migrate')
    local('python manage.py collectstatic --noinput')
    local('touch wsgi.py')



