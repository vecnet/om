#!/usr/bin/env bash

# http://stackoverflow.com/questions/18215973/how-to-check-if-running-as-root-in-a-bash-script
# EUID   Expands to the effective user ID of the current  user,  initialized at shell startup.
# This variable is readonly.
if [ "$EUID" -eq 0 ]
  then echo "Don't run this as root"
  exit
fi

VENV_NAME=`echo $VIRTUAL_ENV | cut -d "/" -f 4`
if [[ `pwd` != *"${VENV_NAME}"* ]]; then
   echo "Are you in right directory???"
   exit
fi

# Parse command line
FORCE_BACKUP=NO
for i in "$@"
do
case $i in
   --backup)
   # Make database backup before updating.
   # (If new Django migrations are found, database backup will be made regardless of this option)
   FORCE_BACKUP=YES
   shift
;;
esac
done

function update
{
    echo "--------------- Starting update ---------------"
    cd src
    echo "Updating: `date`"
    git log -1

    touch django.log
    chmod 660 django.log
    git pull
#    if [ $? -ne 0 ]; then
#       echo "git pull failed"
#       echo "make sure you ran ssh-add ~/.ssh/github"
#       exit 1
#    fi
    echo "Removing .pyc files"
    find . -name \*.pyc -delete
    # Dependencies should be installed before running showmigrations
    pip install -r requirements/production.txt
    # Make database backup if migrations are required or --backup option is specified
    python manage.py showmigrations --list | grep "\[ \]"
    if [ $? -ne 1 ] || [ ${FORCE_BACKUP} == YES ] ; then
        echo "Unapplied migrations found, making DB backup"
        python manage.py backup_db
    else
        echo "All migrations has been applied, no DB backup"
    fi
    python manage.py migrate
    python manage.py collectstatic --noinput
    touch wsgi.py
    python manage.py check --deploy
    echo "--------------- Update complete ---------------"
}

# Append output of update command to the beginning of update.log flie
mv update.log update.log.bak
update | tee update.log
cat update.log.bak >> update.log