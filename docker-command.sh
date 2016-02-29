echo "Applying database migrations."
python manage.py migrate auth --noinput
python manage.py migrate --noinput
sh load-fixtures.sh
sh delete-test-user.sh
sh create-test-user.sh
python manage.py runserver 0.0.0.0:8000
