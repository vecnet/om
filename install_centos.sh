#!/usr/bin/env bash

# http://stackoverflow.com/questions/18215973/how-to-check-if-running-as-root-in-a-bash-script
# EUID   Expands to the effective user ID of the current  user,  initialized at shell startup.
# This variable is readonly.
if [ "${EUID}" -ne 0 ]
  then echo "Please run as root"
  exit
fi

yum install xerces-c gsl git nginx python-pip python-devel
# Repository for PostgreSQL 9.6
yum install https://download.postgresql.org/pub/repos/yum/9.6/redhat/rhel-7-x86_64/pgdg-redhat96-9.6-3.noarch.rpm
yum install postgresql96-devel postgresql96
/usr/pgsql-9.6/bin/postgresql96-setup initdb

sudo cp /var/lib/pgsql/9.6/data/pg_hba.conf /var/lib/pgsql/9.6/data/pg_hba.conf.bak
sudo sh -c 'echo "local   all    all     ident" > /var/lib/pgsql/9.6/data/pg_hba.conf'
sudo sh -c 'echo "host    all             all             all    md5">> /var/lib/pgsql/9.6/data/pg_hba.conf'

systemctl enable postgresql-9.6
systemctl start postgresql-9.6

sudo systemctl start postgresql
sudo -u postgres sh -c 'createdb om'
sudo -u postgres psql -c "CREATE USER om WITH PASSWORD 'om'"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE \"om\" to om;"
sudo systemctl restart postgresql-9.6

