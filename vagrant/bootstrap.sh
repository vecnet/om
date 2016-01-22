#!/bin/sh
WEB_DIR=/opt/web
VIRTUAL_ENVS_DIR=/opt/venvs
VIRTUAL_ENV_DIR=$VIRTUAL_ENVS_DIR/om
SYNCED_DIR=/opt/synced/om

mkdir $WEB_DIR
mkdir $VIRTUAL_ENVS_DIR
mkdir $VIRTUAL_ENV_DIR

yum -y -q install gcc git libxml2-devel libxslt-devel httpd mod_wsgi python-devel postgresql-devel postgresql-server postgresql-contrib postgresql-client python-psycopg2
yum -y -q install gsl xerces-c

sudo postgresql-setup initdb
systemctl enable postgresql.service
sudo sh -c 'echo "local   all             all                                     peer" > /var/lib/pgsql/data/pg_hba.conf'
sudo sh -c 'echo "host    all             all             all    md5">> /var/lib/pgsql/data/pg_hba.conf'
sudo sh -c "echo listen_addresses = \\'*\\' >> /var/lib/pgsql/data/postgresql.conf"
systemctl start postgresql.service
sudo -u postgres sh -c 'createdb om'
sudo -u postgres psql -c "CREATE USER om WITH PASSWORD 'om'"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE om to om;"
systemctl restart postgresql.service

echo "127.0.0.1   om.dev" >> /etc/hosts

mv /etc/httpd/conf/httpd.conf{,.orig}
cp /vagrant/httpd.conf /etc/httpd/conf/httpd.conf

cp -r $SYNCED_DIR $WEB_DIR/
WEB_APP_DIR=$WEB_DIR/om

curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
python get-pip.py
rm get-pip.py

pip install virtualenv
pushd $VIRTUAL_ENVS_DIR
virtualenv om
source om/bin/activate
pip install -r $WEB_APP_DIR/requirements.txt
pip install -r /vagrant/extra-requirements.txt

cp /vagrant/settings_local.py $WEB_APP_DIR/website/

pushd $WEB_APP_DIR

python manage.py migrate auth --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput

python manage.py loaddata AnophelesSnippets
python manage.py loaddata BaselineScenarios
python manage.py loaddata DemographicsSnippets
python manage.py loaddata Interventions

popd

sh /vagrant/create-test-user.sh

touch $WEB_APP_DIR/wsgi.py

chown -R apache $WEB_APP_DIR

systemctl enable httpd
systemctl restart httpd
