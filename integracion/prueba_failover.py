#!/usr/bin/env python3
"""Ensayo explícito de promoción y retorno con reseed y conservación de datos."""
import argparse
import base64
import concurrent.futures
from datetime import datetime, timezone
import json
import shlex
import time
import urllib.request
import operaciones as op
from preparar_continuidad import app_environment, web_instances, web_script

EVIDENCE=op.ROOT/'integracion/evidencias/20261104/failover.json'


def aws_query(sql):
    script='set -e; sudo -u postgres psql -X -At -v ON_ERROR_STOP=1 -d awsacademydb -c '+shlex.quote(sql)
    return op.ssm(op.state('aws')['db_instance'],script,timeout=90)['out']


def gcp_query(sql):
    return op.ssh('set -e; sudo -u postgres psql -h 127.0.0.1 -X -At -v ON_ERROR_STOP=1 -d awsacademydb -c '+shlex.quote(sql),timeout=90)


def health(url):
    try:
        request=urllib.request.Request(url,headers={'Cache-Control':'no-cache'})
        with urllib.request.urlopen(request,timeout=8) as response:
            raw=response.read().decode()
            return {'http':response.status,'datos':json.loads(raw) if raw.startswith('{') else {'portal_nexoandes':'NexoAndes' in raw}}
    except Exception as error:
        return {'http':getattr(error,'code',None),'error':type(error).__name__}


def configure_webs(host):
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        tasks={pool.submit(op.ssm,i,web_script(host),timeout=240):i for i in web_instances()}
        return {tasks[t]:t.result() for t in concurrent.futures.as_completed(tasks)}


def reseed(target,host):
    secret=op.private_settings()['replication_password'];archive=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    pgpass='/var/lib/pgsql/.pgpass' if target=='aws' else '/var/lib/postgresql/.pgpass'
    basebackup='/usr/bin/pg_basebackup' if target=='aws' else '/usr/lib/postgresql/15/bin/pg_basebackup'
    service='postgresql' if target=='aws' else 'nexoandes-postgresql'
    script='set -euo pipefail\n'
    script+=op.write_remote(pgpass,f'{host}:5432:replication:nexo_replicator:{secret}\n')
    script+=f'chown postgres:postgres {pgpass}\nsystemctl stop {service}\n'
    script+=f'mv /srv/postgresql/data /srv/postgresql/antes-reseed-{archive}\n'
    # La copia anterior se conserva. Si la nueva copia falla, el nodo permanece
    # detenido; nunca se inicia automáticamente como primario divergente.
    slot=' -C -S nexoandes_gcp' if target=='gcp' else ''
    script+=f'sudo -u postgres env PGPASSFILE={pgpass} {basebackup} -h {host} -U nexo_replicator -D /srv/postgresql/data -R -X stream{slot}\n'
    script+="sed -i '/^primary_conninfo[[:space:]]*=/d; /^primary_slot_name[[:space:]]*=/d' /srv/postgresql/data/postgresql.auto.conf\n"
    setting=f"primary_conninfo = 'host={host} port=5432 user=nexo_replicator passfile={pgpass} application_name=nexoandes_{target}'\n"
    if target=='gcp':setting+="primary_slot_name = 'nexoandes_gcp'\n"
    script+='cat >> /srv/postgresql/data/postgresql.auto.conf <<\'CONNECTION\'\n'+setting+'CONNECTION\n'
    if target=='aws':script+='systemctl unmask --runtime postgresql\n'
    script+=f'systemctl start {service}\n'
    script+='echo RESEED_CONSERVANDO_COPIA_ANTERIOR\n'
    return op.ssm(op.state('aws')['db_instance'],script,timeout=240) if target=='aws' else op.ssh(script,timeout=240)


def restore_test(source):
    backup=json.loads((op.ROOT/'integracion/evidencias/20261104/respaldos.json').read_text())
    file=op.PRIVATE/'respaldos'/(backup['objeto'].split('/')[-1]+'.'+source)
    content=file.read_bytes()
    if len(content)>100000:raise RuntimeError('Dump excede el límite del transporte administrativo de esta prueba')
    encoded=base64.b64encode(content).decode();name='nexo_restore_20261104_'+source
    script=f'''set -euo pipefail
printf '%s' {shlex.quote(encoded)} | base64 -d > /tmp/{name}.dump
chmod 600 /tmp/{name}.dump
chown postgres:postgres /tmp/{name}.dump
sudo -u postgres dropdb -h 127.0.0.1 --if-exists {name}
sudo -u postgres createdb -h 127.0.0.1 {name}
sudo -u postgres pg_restore -h 127.0.0.1 -d {name} /tmp/{name}.dump
sudo -u postgres psql -h 127.0.0.1 -At -d {name} -c 'SELECT count(*),max(id) FROM nexoandes_continuity_probe'
sudo -u postgres dropdb -h 127.0.0.1 {name}
rm /tmp/{name}.dump
'''
    return {'fuente':source,'resultado':op.ssh(script,timeout=120),'bytes':len(content),'objeto':backup['objeto']}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--ejecutar',action='store_true');args=parser.parse_args()
    if not args.ejecutar:parser.error('Usa --ejecutar para el ensayo controlado que cambia roles y disponibilidad')
    op.assert_aws_identity();aws=op.state('aws');gcp=op.state('gcp')
    op.aws(['autoscaling','suspend-processes','--auto-scaling-group-name','nexoandes-web','--scaling-processes','AlarmNotification'])
    result={'utc':datetime.now(timezone.utc).isoformat(),'tipo':'ensayo manual mediante script; sin detector/promotor autónomo','fases':[]}
    def checkpoint(phase,**values):
        result['fases'].append({'fase':phase,'utc':datetime.now(timezone.utc).isoformat(),**values})
        EVIDENCE.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(phase,flush=True)
    try:
        if gcp_query('SELECT pg_is_in_recovery()')!='t':raise RuntimeError('GCP no es réplica; no se inicia el ensayo')
        checkpoint('sondas_preparadas',web=configure_webs(aws['db_ip']))
        aws_query("INSERT INTO nexoandes_continuity_probe(etiqueta) VALUES ('antes-failover-20261104')")
        marker=int(aws_query('SELECT max(id) FROM nexoandes_continuity_probe'))
        for _ in range(15):
            if int(gcp_query('SELECT max(id) FROM nexoandes_continuity_probe'))==marker:break
            time.sleep(1)
        else:raise RuntimeError('El marcador no llegó a la réplica')
        checkpoint('replica_verificada',marcador=marker,estado=aws_query("SELECT state||'|'||coalesce(replay_lag::text,'0') FROM pg_stat_replication"))
        started=time.monotonic()
        op.ssm(aws['db_instance'],'set -e; systemctl stop nexoandes-backup.timer; systemctl stop postgresql; systemctl mask --runtime postgresql; echo PRIMARIO_AISLADO',timeout=90)
        checkpoint('aws_aislado',sonda_aws=health(aws['url']+'/health'))
        if gcp_query('SELECT pg_promote(true,60)')!='t':raise RuntimeError('La promoción no terminó')
        response=health('http://'+gcp['vm_ip']+'/health')
        if response.get('http')!=200 or response['datos']['database']['recovery']:raise RuntimeError('GCP no sirve como primario')
        checkpoint('gcp_promovido',rto_observado_segundos=round(time.monotonic()-started,2),sonda=response,registros_prueba_perdidos=marker-response['datos']['database']['probe'])
        gcp_query("INSERT INTO nexoandes_continuity_probe(etiqueta) VALUES ('escrito-en-gcp-20261104')")
        gcp_marker=int(gcp_query('SELECT max(id) FROM nexoandes_continuity_probe'))
        web=configure_webs('10.30.1.10');response=health(aws['url']+'/health')
        if response.get('http')!=200 or response['datos']['database']['recovery'] or response['datos']['database']['probe']!=gcp_marker:
            raise RuntimeError('La aplicación AWS no confirmó la conexión al primario GCP')
        checkpoint('aplicacion_reconectada',web=web,sonda_aws=response,marcador_gcp=gcp_marker)
        instances=web_instances()
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                list(pool.map(lambda i:op.ssm(i,'systemctl stop httpd; echo WEB_DETENIDA',timeout=30),instances))
            checkpoint('portal_alternativo_sin_web_aws',aws=health(aws['url']+'/?prueba_contingencia='+str(time.time_ns())),gcp=health('http://'+gcp['vm_ip']+'/'),sonda_gcp=health('http://'+gcp['vm_ip']+'/health'),alcance='Se detuvieron procesos web y BD; no se simuló una caída real del proveedor ni del plano de administración')
        finally:
            for instance in instances:op.ssm(instance,'systemctl start httpd; echo WEB_RESTAURADA',timeout=40)
        checkpoint('restauracion_en_gcp',pruebas=[restore_test('azure'),restore_test('gcp')])
        # Habilitar réplica inversa por el túnel para un retorno sin perder la
        # escritura efectuada en GCP. La copia anterior AWS permanece en disco.
        gcp_query('SELECT pg_reload_conf()')
        op.ssh("set -e; HBA=/srv/postgresql/data/pg_hba.conf; grep -q '^host replication nexo_replicator 10.10.20.35/32' \"$HBA\" || echo 'host replication nexo_replicator 10.10.20.35/32 scram-sha-256' >> \"$HBA\"; sudo -u postgres psql -h 127.0.0.1 -At -c 'SELECT pg_reload_conf()'",timeout=60)
        checkpoint('aws_resembrado_como_replica',resultado=reseed('aws','10.30.1.10'))
        for _ in range(15):
            values=aws_query('SELECT pg_is_in_recovery(),max(id) FROM nexoandes_continuity_probe')
            if values==f't|{gcp_marker}':break
            time.sleep(1)
        else:raise RuntimeError('AWS no recuperó el marcador escrito en GCP')
        op.ssh('set -e; systemctl stop nexoandes-postgresql; echo GCP_DETENIDO_PARA_RETORNO',timeout=60)
        if aws_query('SELECT pg_promote(true,60)')!='t':raise RuntimeError('AWS no pudo recuperar el rol primario')
        checkpoint('aws_primario_restablecido',datos=aws_query('SELECT pg_is_in_recovery(),max(id) FROM nexoandes_continuity_probe'),web=configure_webs(aws['db_ip']))
        checkpoint('gcp_resembrado_como_replica',resultado=reseed('gcp',aws['db_ip']))
        op.ssh(op.write_remote('/etc/nexoandes/app.env',app_environment('127.0.0.1','gcp'))+'systemctl restart nexoandes-app',timeout=45)
        op.ssm(aws['db_instance'],'systemctl start nexoandes-backup.timer; echo RESPALDOS_REACTIVADOS',timeout=40)
        result['final']={'aws':health(aws['url']+'/health'),'gcp':health('http://'+gcp['vm_ip']+'/health'),'marcador_preservado':gcp_marker}
        if result['final']['aws'].get('http')!=200 or result['final']['gcp'].get('http')!=200:raise RuntimeError('Las sondas finales no están saludables')
        result['completo']=True;checkpoint('ensayo_y_retorno_completos')
    except Exception as error:
        result['completo']=False;result['error']=str(error)
        EVIDENCE.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        raise
    finally:
        op.aws(['autoscaling','resume-processes','--auto-scaling-group-name','nexoandes-web','--scaling-processes','AlarmNotification'])


if __name__=='__main__':main()
