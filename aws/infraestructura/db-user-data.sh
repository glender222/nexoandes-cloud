#!/bin/bash
yum update -y
yum install -y postgresql15-server
postgresql-setup --initdb
systemctl enable postgresql
systemctl start postgresql
IP=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)
echo "listen_addresses = '*'" >> /var/lib/pgsql/data/postgresql.conf
echo "host all all 10.10.0.0/16 md5" >> /var/lib/pgsql/data/pg_hba.conf
systemctl restart postgresql
sudo -u postgres psql -c "CREATE USER awsacademy WITH PASSWORD 'AWsAcademy2026!';"
sudo -u postgres psql -c "CREATE DATABASE awsacademydb OWNER awsacademy;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE awsacademydb TO awsacademy;"
