CREATE_USER_CMD="from django.contrib.auth.models import User; User.objects.create_superuser('om', '', 'om'); exit()"
echo $CREATE_USER_CMD | /usr/local/bin/python manage.py shell
