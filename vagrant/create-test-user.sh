PROJECT_ROOT=/opt/web/om
CREATE_USER_CMD="from django.contrib.auth.models import User; User.objects.create_superuser('om', '', 'om'); exit()"
export DJANGO_SETTINGS_MODULE="website.settings"
echo $CREATE_USER_CMD | python $PROJECT_ROOT/manage.py shell
