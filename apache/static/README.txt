Do not put files to this folder manually. Use manage.py collectstatic to collect files from apps static/
subdirectories instead.
This folder should be specified as settings.STATIC_ROOT, for example
STATIC_ROOT = os.path.join(BASE_DIR, 'apache', 'static')