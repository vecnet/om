DELETE_USER_CMD="from django.contrib.auth.models import User; user = User.objects.get(username='om'); user.delete(); exit()"
echo $DELETE_USER_CMD | /usr/local/bin/python manage.py shell
