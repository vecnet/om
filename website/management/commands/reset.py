# Copyright (C) 2015, University of Notre Dame
# All rights reserved
import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django import db

# from website.database_apps.database_manager.utils.backup_and_restore_functions import backup
from website.management.commands.backup_db import backup


class Command(BaseCommand):
    def add_arguments(self, parser):

        # Named (optional) arguments
        parser.add_argument(
            "--nobackup",
            action="store_true",
            dest="nobackup",
            default=False,
            help="Do not backup database before reset"
        )
        parser.add_argument(
            "--nomigrate",
            action="store_true",
            dest="nomigrate",
            default=False,
            help="Do not run migrate command"
        )

    def handle(self, *args, **options):
        """
        Main function for the management command.
        Drop all tables, run migrate command and populate database with fake data
        """
        engine = db.connections.databases["default"]["ENGINE"]
        cursor = connection.cursor()

        if not options["nobackup"]:
            print("Making database backup")
            result, message = backup("reset", os.environ.get("USER", "unknown"))
            if not result:
                print("Failed to backup the database, %s" % message)
                return
            print("Backup complete, filename %s" % message)

        print("Dropping all tables")
        if engine == "django.db.backends.sqlite3":
            # List of all tables in SQLite database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            tables = [row[0] for row in cursor.fetchall()]
            for table in tables:
                if table != "sqlite_sequence":
                    # table sqlite_sequence may not be dropped
                    cursor.execute("DROP TABLE '%s'" % table)
        elif engine == "django.db.backends.postgresql_psycopg2" or engine == "django.db.backends.postgresql":
            # List of all tables in PostgreSQL database
            # http://dba.stackexchange.com/questions/1285/how-do-i-list-all-databases-and-tables-using-psql
            # Note you can't drop database here - because connection.cursor() is using it!
            # Thus deleting all tables and re-creating them using migrate command later
            cursor.execute("SELECT table_schema,table_name FROM information_schema.tables ORDER BY table_schema, table_name;")  # noqa
            tables = cursor.fetchall()
            for table in tables:
                if table[0] == "public":
                    cursor.execute("DROP TABLE %s.%s CASCADE;" % (table[0], table[1]))
        else:
            raise RuntimeError("Unsupported database engine %s" % engine)

        if not options["nomigrate"]:
            print("Running migrate command")
            call_command("migrate")
