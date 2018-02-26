package 'gsl'
package 'xerces-c'
package 'httpd'
package 'mod_wsgi'
package 'python-pip'
package 'git'
package 'vim'

bash 'postgresql respository' do
  code <<-EOH
  yum install -y https://download.postgresql.org/pub/repos/yum/9.6/redhat/rhel-7-x86_64/pgdg-redhat96-9.6-3.noarch.rpm
EOH
  not_if {::File.exist?('/etc/yum.repos.d/pgdg-96-redhat.repo')}
end

package 'postgresql96-server'
package 'postgresql96-devel'


bash 'postgresql initdb' do
  code <<-EOH
  /usr/pgsql-9.6/bin/postgresql96-setup initdb
EOH
  not_if {::File.exist?('/var/lib/pgsql/9.6/data/')}
end

service 'postgresql-9.6' do
  action [:enable, :start]
end

bash 'postgresql create user' do
  code <<-EOH
  sudo -u postgres sh -c 'createdb om'
  sudo -u postgres psql -c "CREATE USER om WITH PASSWORD 'om'"
  sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE \"om\" to om;"
EOH
  ignore_failure true
end

file '/var/lib/pgsql/9.6/data/pg_hba.conf' do
  owner 'postgres'
  group 'postgres'
  mode '600'
  content <<-EOH
local   all    all     ident
host    all             all             all    md5
EOH
end

directory 'opt/portal/aws.vecnet.org' do
  owner 'root'
  group 'apache'
  recursive true
end

git '/opt/portal/aws.vecnet.org' do
  group 'apache'
  repository 'https://github.com/vecnet/om'
  action :sync
end

file '/opt/portal/aws.vecnet.org/config_local.py' do
  group 'apache'
  mode '640'
  content <<-EOH
import os

settings_module="website.settings.aws"

os.environ["SECRET_KEY"] = "lkl39#;l=01,<ML;lodfsd;lkOP(aa;dsf90adfsadfksldfjp90sdflsklilsdfslklkj"
os.environ["DATABASE_NAME"] = "om"
os.environ["DATABASE_USER"] = "om"
os.environ["DATABASE_PASSWORD"] = "om"
EOH
end

file '/opt/portal/aws.vecnet.org/django.log' do
   group 'apache'
   mode '660'
end

bash 'Install python packages' do
  code 'pip install -r /opt/portal/aws.vecnet.org/requirements/aws.txt'
end

service 'httpd' do
  action [:enable, :start]
end
