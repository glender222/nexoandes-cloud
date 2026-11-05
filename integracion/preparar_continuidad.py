#!/usr/bin/env python3
"""Preparar réplica y sondas de demostración; no sustituye un sistema de pedidos."""
from datetime import datetime, timezone
import concurrent.futures
import json
from pathlib import Path
import operaciones as op


def app_environment(host,site):
    settings=op.private_settings()
    return f'PGHOST={host}\nPGPORT=5432\nPGDATABASE=awsacademydb\nPGUSER=nexo_app\nPGPASSWORD={settings["app_password"]}\nNEXO_SITE={site}\n'


def primary_script():
    secret=op.private_settings()
    return f'''set -euo pipefail
/usr/local/sbin/nexoandes-backup
sudo -u postgres psql -v ON_ERROR_STOP=1 <<'SQL'
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='nexo_replicator') THEN
    CREATE ROLE nexo_replicator REPLICATION LOGIN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='nexo_app') THEN
    CREATE ROLE nexo_app LOGIN;
  END IF;
END $$;
ALTER ROLE nexo_replicator PASSWORD '{secret['replication_password']}';
ALTER ROLE nexo_app PASSWORD '{secret['app_password']}';
ALTER SYSTEM SET wal_log_hints='on';
ALTER SYSTEM SET max_slot_wal_keep_size='256MB';
ALTER SYSTEM SET wal_keep_size='64MB';
SQL
sudo -u postgres psql -v ON_ERROR_STOP=1 -d awsacademydb <<'SQL'
CREATE TABLE IF NOT EXISTS public.nexoandes_continuity_probe (
 id bigserial PRIMARY KEY, etiqueta text NOT NULL, creado timestamptz NOT NULL DEFAULT clock_timestamp()
);
GRANT CONNECT ON DATABASE awsacademydb TO nexo_app;
GRANT USAGE ON SCHEMA public TO nexo_app;
GRANT SELECT ON public.nexoandes_continuity_probe TO nexo_app;
INSERT INTO public.nexoandes_continuity_probe(etiqueta) VALUES ('preparacion-20261104');
SQL
HBA=/srv/postgresql/data/pg_hba.conf
grep -q '^host replication nexo_replicator 10.30.1.10/32' "$HBA" || echo 'host replication nexo_replicator 10.30.1.10/32 scram-sha-256' >> "$HBA"
grep -q '^host awsacademydb nexo_app 10.30.1.10/32' "$HBA" || echo 'host awsacademydb nexo_app 10.30.1.10/32 scram-sha-256' >> "$HBA"
systemctl restart postgresql
sudo -u postgres psql -At -d awsacademydb -c 'SELECT count(*),max(id) FROM nexoandes_continuity_probe'
'''


def replica_script(primary):
    password=op.private_settings()['replication_password']
    script='set -euo pipefail\ntest -f /var/lib/nexoandes-bootstrap-ready\n'
    script+=op.write_remote('/var/lib/postgresql/.pgpass',f'{primary}:5432:replication:nexo_replicator:{password}\n')
    script+='chown postgres:postgres /var/lib/postgresql/.pgpass\n'
    script+=f'''if [[ ! -f /srv/postgresql/data/PG_VERSION ]]; then
  sudo -u postgres /usr/lib/postgresql/15/bin/pg_basebackup -h {primary} -U nexo_replicator -D /srv/postgresql/data -R -X stream -C -S nexoandes_gcp
fi
test -f /srv/postgresql/data/standby.signal || {{ echo 'GCP ya es primario: no se sobrescribe'; exit 2; }}
systemctl start nexoandes-postgresql
'''
    script+=op.write_remote('/etc/nexoandes/app.env',app_environment('127.0.0.1','gcp'))
    script+=op.write_remote('/opt/nexoandes/health_app.py',(op.ROOT/'integracion/health_app.py').read_text(),mode='644')
    script+='systemctl restart nexoandes-app\nsudo -u postgres psql -h 127.0.0.1 -At -d awsacademydb -c "SELECT pg_is_in_recovery(),count(*),max(id) FROM nexoandes_continuity_probe"\n'
    return script


def web_script(host):
    script='set -euo pipefail\ndnf install -y postgresql15 >/dev/null\n'
    script+=op.write_remote('/opt/nexoandes/health_app.py',(op.ROOT/'integracion/health_app.py').read_text(),mode='644')
    script+=op.write_remote('/etc/nexoandes/app.env',app_environment(host,'aws'))
    script+=op.write_remote('/etc/systemd/system/nexoandes-app.service','''[Unit]
Description=Sonda PostgreSQL NexoAndes
After=network-online.target
[Service]
User=nobody
EnvironmentFile=/etc/nexoandes/app.env
Environment=NEXO_BIND=127.0.0.1 NEXO_PORT=8081
ExecStart=/usr/bin/python3 /opt/nexoandes/health_app.py
Restart=always
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
[Install]
WantedBy=multi-user.target
''',mode='644')
    script+=op.write_remote('/etc/httpd/conf.d/nexoandes-health.conf','ProxyPass "/health" "http://127.0.0.1:8081/health"\nProxyPassReverse "/health" "http://127.0.0.1:8081/health"\n',mode='644')
    script+='systemctl daemon-reload\nsystemctl enable nexoandes-app >/dev/null\nsystemctl restart nexoandes-app\nhttpd -t\nsystemctl reload httpd\ncurl --fail --silent --retry 5 --retry-delay 1 --retry-all-errors http://127.0.0.1/health\n'
    return script


def web_instances():
    groups=op.aws(['autoscaling','describe-auto-scaling-groups','--auto-scaling-group-names','nexoandes-web'])
    return [i['InstanceId'] for i in groups['AutoScalingGroups'][0]['Instances'] if i['LifecycleState']=='InService']


def main():
    op.assert_aws_identity();aws=op.state('aws')
    result={'utc':datetime.now(timezone.utc).isoformat()}
    result['primary']=op.ssm(aws['db_instance'],primary_script(),timeout=180)
    print('Primario preparado y respaldo previo generado.',flush=True)
    result['replica']=op.ssh(replica_script(aws['db_ip']),timeout=240)
    print('Réplica iniciada:',result['replica'],flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        tasks={pool.submit(op.ssm,i,web_script(aws['db_ip']),timeout=240):i for i in web_instances()}
        result['web']={tasks[f]:f.result() for f in concurrent.futures.as_completed(tasks)}
    path=op.ROOT/'integracion/evidencias/20261104/preparacion-continuidad.json'
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('Sondas instaladas en las dos instancias web; evidencia guardada.')


if __name__=='__main__':main()
