echo "Applying database migrations."
python /app/manage.py migrate auth --noinput
python /app/manage.py migrate --noinput
sh /app/docker/load-fixtures.sh
sh /app/docker/delete-test-user.sh
sh /app/docker/create-test-user.sh
python /app/manage.py runserver 0.0.0.0:8000
