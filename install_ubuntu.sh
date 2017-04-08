#!/usr/bin/env bash

DB_NAME=om
SITE_URL=aws.vecnet.org

# http://stackoverflow.com/questions/18215973/how-to-check-if-running-as-root-in-a-bash-script
# EUID   Expands to the effective user ID of the current  user,  initialized at shell startup.
# This variable is readonly.
if [ "${EUID}" -ne 0 ]
  then echo "Please run as root"
  exit
fi

apt update
apt -y install python-minimal python-pip git
apt -y install openssl libssl-dev
mkdir -p /opt/portal/om
git clone https://github.com/vecnet/om /opt/portal/$SITE_URL
mkdir -p /opt/portal/$SITE_URL/logs
touch /opt/portal/$SITE_URL/django.log
chown -R www-data:www-data /opt/portal/$SITE_URL
pip install -r /opt/portal/$SITE_URL/requirements/aws.txt

cat > /opt/portal/$SITE_URL/config_local.py << EOL
import os

settings_module="website.settings.aws"

os.environ["SECRET_KEY"] = "lkl39#;l=01,<ML;lodfsd;lkOP(aa;dsf90adfsadfksldfjp90sdflsklilsdfslklkj"
os.environ["DATABASE_NAME"] = "om"
os.environ["DATABASE_USER"] = "om"
os.environ["DATABASE_PASSWORD"] = "om"
EOL

#################################
# Configure postgresql
#################################
apt -y install postgresql postgresql-contrib libpq-dev
sudo -u postgres createdb ${DB_NAME}
sudo -u postgres psql -c "CREATE USER ${DB_NAME} WITH PASSWORD '${DB_NAME}'"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE \"${DB_NAME}\" to ${DB_NAME};"


#############################
# Configure apache - no SSL, sufficient for let's encrypt it
#############################

apt -y install apache2 apache2-dev libapache2-mod-wsgi
a2enmod rewrite
a2enmod ssl
a2enmod wsgi
# To activate new configuration, you need to run:
service apache2 restart
mkdir -p /etc/apache2/ssl/
cat > /etc/apache2/sites-available/$SITE_URL.conf << EOL
<VirtualHost *:80>
  ServerName $SITE_URL
  Alias /.well-known/ /opt/portal/$SITE_URL/apache/.well-known/
  RewriteEngine On
  RewriteCond %{HTTPS} off
  # Leave /.well-known/ directory open for let's encrypt it client
  RewriteCond %{REQUEST_URI} !^/.well-known
  RewriteRule (.*) https://%{HTTP_HOST}%{REQUEST_URI}?%{QUERY_STRING}

  <Directory /opt/portal/$SITE_URL/apache/.well-known/>
        Options -Indexes +FollowSymLinks
        AllowOverride None
        Require all granted
  </Directory>


</VirtualHost>
EOL

a2ensite $SITE_URL.conf
a2dissite 000-default.conf
service apache2 reload

##########################
# Firewall configuration
##########################
ufw allow http
ufw allow https

###########################
## Let's encrypt it
###########################
#sh -c "curl https://get.acme.sh | sh"
#/root/.acme.sh/acme.sh --issue -d $SITE_URL -w /opt/portal/$SITE_URL/apache
#/root/.acme.sh/acme.sh --installcert -d $SITE_URL --certpath /etc/apache2/ssl/$SITE_URL.cer --keypath /etc/apache2/ssl/$SITE_URL.key --fullchainpath /etc/apache2/ssl/$SITE_URL.int.cer --reloadcmd "service apache2 restart"
#
#
###########################
## Finalize apache conf (SSL)
###########################
cat > /etc/apache2/sites-available/$SITE_URL.conf << EOL
<VirtualHost *:80>
  Alias /.well-known/ /opt/portal/$SITE_URL/apache/.well-known/

  <Directory /opt/portal/$SITE_URL/apache/.well-known/>
        Options -Indexes +FollowSymLinks
        AllowOverride None
        Require all granted
  </Directory>

  ServerAdmin avyushko@nd.edu
  CustomLog /opt/portal/$SITE_URL/logs/$SITE_URL.access.log combined
  ErrorLog /opt/portal/$SITE_URL/logs/$SITE_URL.error.log

  DocumentRoot "/opt/portal/$SITE_URL/"
  Alias /static/ /opt/portal/$SITE_URL/apache/static/
  <Directory /$SITE_URL/apache/static/ >
    # Order deny,allow
    # Allow from all
    Require all granted
  </Directory>

  <Directory "/opt/portal/$SITE_URL/">
    Options Includes FollowSymLinks
    AllowOverride all
    # Order allow,deny
    # Allow from all
    Require all granted
  </Directory>

  WSGIDaemonProcess $SITE_URL processes=3  python-path=/opt/portal/$SITE_URL/
  WSGIProcessGroup $SITE_URL
  WSGIScriptAlias / /opt/portal/$SITE_URL/wsgi.py

  TraceEnable Off

</VirtualHost>
EOL


#cat > /etc/apache2/sites-available/$SITE_URL.conf << EOL
#<VirtualHost *:80>
#  ServerName $SITE_URL
#  Alias /.well-known/ /opt/portal/$SITE_URL/apache/.well-known/
#  RewriteEngine On
#  RewriteCond %{HTTPS} off
#  # Leave /.well-known/ directory open for let's encrypt it client
#  RewriteCond %{REQUEST_URI} !^/.well-known
#  RewriteRule (.*) https://%{HTTP_HOST}%{REQUEST_URI}?%{QUERY_STRING}
#
#  <Directory /opt/portal/$SITE_URL/apache/.well-known/>
#        Options -Indexes +FollowSymLinks
#        AllowOverride None
#        Require all granted
#  </Directory>
#
#
#</VirtualHost>
#
#<VirtualHost *:443>
#  ServerAdmin avyushko@nd.edu
#  ServerName $SITE_URL
#  CustomLog /opt/portal/$SITE_URL/logs/$SITE_URL.access.log combined
#  ErrorLog /opt/portal/$SITE_URL/logs/$SITE_URL.error.log
#
#  SSLEngine on
#
#  SSLCipherSuite HIGH:MEDIUM:!aNULL:!MD5:!RC4
#  SSLCertificateFile /etc/apache2/ssl/$SITE_URL.crt
#  SSLCertificateKeyFile /etc/apache2/ssl/$SITE_URL.key
#  SSLCertificateChainFile /etc/apache2/ssl/$SITE_URL.int.cer
#
#
#  DocumentRoot "/opt/portal/$SITE_URL/"
#  Alias /static/ /opt/portal/$SITE_URL/apache/static/
#  <Directory /$SITE_URL/apache/static/ >
#    # Order deny,allow
#    # Allow from all
#    Require all granted
#  </Directory>
#
#  <Directory "/opt/portal/$SITE_URL/">
#    Options Includes FollowSymLinks
#    AllowOverride all
#    # Order allow,deny
#    # Allow from all
#    Require all granted
#  </Directory>
#
#  WSGIDaemonProcess $SITE_URL processes=3  python-path=/opt/portal/$SITE_URL/:/usr/lib/python2.7/ home=/opt/portal/$SITE_URL/  display-name=$SITE_URL
#  WSGIProcessGroup $SITE_URL
#  WSGIScriptAlias / /opt/portal/$SITE_URL/wsgi.py
#
#  TraceEnable Off
#
#</VirtualHost>
#EOL


service apache2 restart