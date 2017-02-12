# Copyright (C) 2016, University of Notre Dame
# All rights reserved


from django.core.management.base import BaseCommand, CommandError
from django import db
import os
import shutil
import subprocess

def restore(filename):
    """ If postgresql is used as database engine, this function calls pg_dump command
    :param filename: pg_dump/sqlite backup file
    :return:
    """
    engine = db.connections.databases["default"]["ENGINE"]

    if engine == "django.db.backends.sqlite3":
        shutil.copyfile(filename, db.connections.databases["default"]["NAME"])
        return True, filename
    elif engine == "django.db.backends.postgresql_psycopg2" or engine == "django.db.backends.postgresql":
        # Database should exist and have permission for the user to create tables on it
        command = "pg_restore -h %s -U %s -F c -d %s %s" % \
                  (db.connections.databases["default"]["HOST"],
                   db.connections.databases["default"]["USER"],
                   db.connections.databases["default"]["NAME"],
                   filename,
                   )
        ret_code = subprocess.call(command,
                                   env=dict(os.environ, PGPASSWORD=db.connections.databases["default"]["PASSWORD"]),
                                   shell=True)
        if ret_code != 0:
            return False, "pg_restore command failed, ret_code %s" % ret_code

        return True, filename
    else:
        return False, "Engine %s is not supported" % engine


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("filename", type=str)

    def handle(self, *args, **options):
        filename = options["filename"]
        print("Restoring database %s from %s" % (db.connections.databases["default"]["NAME"], filename))
        result, message = restore(filename)

        if result:
            print("Database restored successfully, filename %s" % message)
        else:
            # If a management command is called from code through call_command,
            # it's up to you to catch the exception when needed.
            raise CommandError(message)
