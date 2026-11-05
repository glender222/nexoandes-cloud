#!/usr/bin/env python3
"""Configurar Supabase autohospedado en la instancia Terraform, sin secretos publicos."""
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import shlex
import subprocess
import tarfile
import time
import operaciones as op

BASE=op.ROOT/'integracion/supabase'
spec=importlib.util.spec_from_file_location('supabase_preparar',BASE/'preparar.py')
preparer=importlib.util.module_from_spec(spec);spec.loader.exec_module(preparer)
PRIVATE=preparer.PRIVATE
EVIDENCE=op.ROOT/'integracion/evidencias/20261104/supabase'


def install_script(bucket,key,sha):
    script=f'''set -euo pipefail
test -f /var/lib/nexoandes-supabase-host-ready
mountpoint -q /srv/supabase
umask 077
aws s3api get-object --region us-east-1 --bucket {shlex.quote(bucket)} --key {shlex.quote(key)} /tmp/nexoandes-supabase.tar.gz >/dev/null
echo '{sha}  /tmp/nexoandes-supabase.tar.gz' | sha256sum -c - >/dev/null
tar -xzf /tmp/nexoandes-supabase.tar.gz -C /srv/supabase
rm /tmp/nexoandes-supabase.tar.gz
chmod 700 /srv/supabase
chmod 600 /srv/supabase/.env
cd /srv/supabase
docker compose config --quiet
docker compose pull --quiet
IMAGE=$(docker compose config --images | grep '^supabase/postgres:')
if [[ ! -f volumes/db-config/supautils.conf ]]; then
  install -d volumes/db-config
  TEMP=$(docker create --entrypoint /bin/true "$IMAGE")
  docker cp -a "$TEMP:/etc/postgresql-custom/." volumes/db-config/
  docker rm -v "$TEMP" >/dev/null
fi
OWNER=$(docker run --rm --entrypoint /bin/sh "$IMAGE" -c 'printf "%s:%s" "$(id -u postgres)" "$(id -g postgres)"')
chown -R "$OWNER" volumes/db-config
docker compose up -d --wait --wait-timeout 240
'''
    script+=op.write_remote('/etc/systemd/system/nexoandes-supabase.service','''[Unit]
Description=Supabase NexoAndes autohospedado
Requires=docker.service
After=docker.service network-online.target
RequiresMountsFor=/srv/supabase
[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/srv/supabase
ExecStart=/usr/bin/docker compose up -d --wait --wait-timeout 240
ExecStop=/usr/bin/docker compose stop
TimeoutStartSec=360
[Install]
WantedBy=multi-user.target
''',mode='644')
    script+='systemctl daemon-reload\nsystemctl enable nexoandes-supabase >/dev/null\nsystemctl start nexoandes-supabase\ndocker compose ps --format json\n'
    script+=op.write_remote('/usr/local/sbin/nexoandes-supabase-backup',(BASE/'respaldo.sh').read_text(),mode='700')
    script+=op.write_remote('/etc/nexoandes/supabase-backup.env','NEXO_BACKUP_BUCKET='+bucket+'\n')
    script+=op.write_remote('/etc/systemd/system/nexoandes-supabase-backup.service','''[Unit]
Description=Respaldo privado de Supabase NexoAndes a S3
After=docker.service network-online.target
[Service]
Type=oneshot
EnvironmentFile=/etc/nexoandes/supabase-backup.env
ExecStart=/usr/local/sbin/nexoandes-supabase-backup
''',mode='644')
    script+=op.write_remote('/etc/systemd/system/nexoandes-supabase-backup.timer','''[Unit]
Description=Respaldo horario Supabase mientras AWS esta activo
[Timer]
OnCalendar=hourly
RandomizedDelaySec=120
Persistent=true
[Install]
WantedBy=timers.target
''',mode='644')
    script+='systemctl daemon-reload\nsystemctl enable --now nexoandes-supabase-backup.timer >/dev/null\n'
    return script


def web_script(settings,internal):
    script='set -euo pipefail\n'
    for source,destination in [('acceso.html','index.html'),('acceso.js','acceso.js'),('estilo.css','estilo.css')]:
        script+=op.write_remote('/var/www/html/acceso/'+destination,(BASE/source).read_text(),mode='644')
    config={'url':settings['SUPABASE_PUBLIC_URL'],'publicKey':settings['SUPABASE_PUBLISHABLE_KEY']}
    script+=op.write_remote('/var/www/html/acceso/config.js','const NEXO_SUPABASE = '+json.dumps(config)+';\n',mode='644')
    script+=op.write_remote('/opt/nexoandes/portal_backend.py',(BASE/'portal_backend.py').read_text(),mode='644')
    script+=op.write_remote('/etc/nexoandes/supabase.env',f'SUPABASE_INTERNAL_URL=http://{internal}:8000\nSUPABASE_PUBLISHABLE_KEY={settings["SUPABASE_PUBLISHABLE_KEY"]}\n')
    script+=op.write_remote('/etc/systemd/system/nexoandes-portal-auth.service','''[Unit]
Description=Validacion de sesion NexoAndes mediante Supabase Auth
After=network-online.target
[Service]
User=nobody
EnvironmentFile=/etc/nexoandes/supabase.env
ExecStart=/usr/bin/python3 /opt/nexoandes/portal_backend.py
Restart=always
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
[Install]
WantedBy=multi-user.target
''',mode='644')
    script+=op.write_remote('/etc/httpd/conf.d/nexoandes-supabase.conf','''ProxyPass "/api/privado" "http://127.0.0.1:8082/api/privado"
ProxyPassReverse "/api/privado" "http://127.0.0.1:8082/api/privado"
<Directory "/var/www/html/acceso">
  Header always set Cache-Control "no-store"
  Header always set X-Content-Type-Options "nosniff"
  Header always set Referrer-Policy "no-referrer"
</Directory>
''',mode='644')
    script+='systemctl daemon-reload\nsystemctl enable --now nexoandes-portal-auth >/dev/null\nsystemctl restart nexoandes-portal-auth\nhttpd -t\nsystemctl reload httpd\n'
    script+="grep -q 'acceso/index.html' /var/www/html/index.html || sed -i 's#</body>#<p style=\"text-align:center\"><a href=\"/acceso/index.html\">Acceso al portal</a></p></body>#' /var/www/html/index.html\n"
    script+='echo PORTAL_AUTH_INSTALADO\n'
    return script


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--ejecutar',action='store_true');args=parser.parse_args()
    if not args.ejecutar:parser.error('Usa --ejecutar para configurar la instancia Supabase ya aprovisionada')
    op.assert_aws_identity();state=op.state('aws');instance=state.get('supabase_instance')
    if not instance or not state.get('https_url'):raise RuntimeError('Primero aplicar Terraform AWS con enable_supabase y HTTPS')
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    settings=preparer.prepare(state['https_url'])
    print('Configuración local validada; credenciales privadas conservadas.',flush=True)
    for _ in range(120):
        managed=op.aws(['ssm','describe-instance-information'])['InstanceInformationList']
        if any(i['InstanceId']==instance and i['PingStatus']=='Online' for i in managed):break
        time.sleep(5)
    else:raise RuntimeError('La instancia Supabase no está disponible por SSM')
    op.ssm(instance,'set -e; for attempt in $(seq 1 120); do test -f /var/lib/nexoandes-supabase-host-ready && { echo HOST_READY; exit 0; }; sleep 5; done; exit 1',timeout=620)
    archive=PRIVATE/'despliegue.tar.gz'
    with tarfile.open(archive,'w:gz') as stream:
        for child in preparer.STACK.iterdir():
            if child.name not in ['.env.old','reset.sh']:stream.add(child,arcname=child.name)
    archive.chmod(0o600);sha=hashlib.sha256(archive.read_bytes()).hexdigest()
    key='supabase-bootstrap/'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.tar.gz'
    upload=op.aws(['s3api','put-object','--bucket',state['bucket'],'--key',key,'--body',str(archive),'--server-side-encryption','AES256','--expected-bucket-owner',op.config()['aws']['cuenta']],timeout=90)
    print('Instalando imágenes fijadas de Supabase en el host privado…',flush=True)
    try:
        installed=op.ssm(instance,install_script(state['bucket'],key,sha),timeout=900)
    finally:
        # Incluso si falla el arranque, retirar solo nuestra version temporal.
        delete=['s3api','delete-object','--bucket',state['bucket'],'--key',key]
        if upload.get('VersionId'):delete+=['--version-id',upload['VersionId']]
        op.aws(delete)
    print('Supabase arrancado; publicando el acceso del portal.',flush=True)
    from preparar_continuidad import web_instances
    result={i:op.ssm(i,web_script(settings,state['supabase_ip']),timeout=150) for i in web_instances()}
    evidence={'utc':datetime.now(timezone.utc).isoformat(),'origen':json.loads((BASE/'ORIGEN.json').read_text()),'instance':instance,'ip_privada':state['supabase_ip'],'volumen':state['supabase_volume'],'url':state['https_url'],'login':state['https_url']+'/acceso/','servicios':installed['out'],'web':result,'autoregistro':'deshabilitado','correos_sms':'sin proveedor de envio configurado','administracion':'Studio externo autenticado HTTPS 8443 y tunel SSM' if state.get('supabase_studio_url') else 'Studio privado; acceso SSM','version_bootstrap_sensible_eliminada':True,'pruebas':'Se verifican separadamente; esta evidencia acredita instalacion'}
    (EVIDENCE/'instalacion.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    print('Instalación terminada; falta prueba real de login y respaldo.',flush=True)


if __name__=='__main__':main()
