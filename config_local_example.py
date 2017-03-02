import os

settings_module = "website.settings.qa"

os.environ["SECRET_KEY"] = "lkl390490adfsadfksldfjp90sdf"
os.environ["ALLOWED_HOSTS"] = "om-qa.vecnet.org"

# os.environ["DATABASE_ENGINE"] = "django.db.backends.postgresql_psycopg2"
os.environ["DATABASE_NAME"] = "qa"
os.environ["DATABASE_USER"] = "qa"
os.environ["DATABASE_PASSWORD"] = "qa"
# os.environ["DATABASE_HOST"] = "127.0.0.1"
# os.environ["DATABASE_PORT"] = "5432"
