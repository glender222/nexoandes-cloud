#!/usr/bin/env python3
"""Reencender la demostración, reconciliar IPs/SSH e instalar la continuidad."""
from datetime import datetime,timezone
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import operaciones as op


def apply(cloud):
    path=op.PRIVATE/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-encender-'+cloud+'.log')
    with path.open('w') as log:
        path.chmod(0o600)
        result=subprocess.run([str(op.ROOT/'nexoandes'),'encender','--nube',cloud],cwd=op.ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=900)
    if result.returncode:raise RuntimeError('Revisar plan/apply privado: '+str(path))
    print(cloud+': infraestructura reconciliada',flush=True)


def main():
    argparse.ArgumentParser(description='Reencender NexoAndes V2 y comprobar continuidad, réplica y HTTPS académico').parse_args()
    op.assert_aws_identity()
    apply('aws');apply('gcp')
    aws=op.state('aws');gcp=op.state('gcp')
    # Al pasar TERMINATED -> RUNNING, Compute puede devolver aún la IP vacía.
    # Releer antes de actualizar los peers evita borrar las reglas UDP de AWS.
    if not gcp.get('vm_ip'):
        apply('gcp')
        gcp=op.state('gcp')
    if not gcp.get('vm_ip'):
        raise RuntimeError('GCP aún no publica IP; no se modificaron los peers VPN')
    for _ in range(90):
        managed=op.aws(['ssm','describe-instance-information'])['InstanceInformationList']
        if any(i['InstanceId']==aws['vpn_instance'] and i['PingStatus']=='Online' for i in managed):break
        time.sleep(3)
    else:raise RuntimeError('El gateway no está disponible por SSM')
    pub=op.ssm(aws['vpn_instance'],'set -e; cloud-init status --wait >/dev/null; command -v ipsec >/dev/null; install -d -m 700 /root/.ssh; test -f /root/.ssh/nexoandes-gcp || ssh-keygen -q -t ed25519 -N "" -C nexoandes-gateway -f /root/.ssh/nexoandes-gcp; cat /root/.ssh/nexoandes-gcp.pub',timeout=300)['out']
    config=op.config();previous=config['gcp']['variables'].get('aws_peer_ip','')
    config['aws']['variables'].update(enable_gcp_vpn=True,gcp_peer_ip=gcp['vm_ip'])
    variables=config['gcp']['variables']
    sources=[s for s in variables['admin_cidrs'] if s!=previous+'/32']
    variables.update(aws_peer_ip=aws['vpn_ip'],ssh_gateway_public_key=pub,admin_cidrs=sorted(set(sources+[aws['vpn_ip']+'/32'])))
    config['gcp']['via_gateway']=True
    op.control.save_json(op.control.CONFIG,config)
    apply('aws');apply('gcp')
    ready=op.ssh('set -e; for attempt in $(seq 1 90); do test -f /var/lib/nexoandes-bootstrap-ready && { echo READY; exit 0; }; sleep 2; done; exit 1',timeout=240)
    print('GCP:',ready,flush=True)
    for script in ['configurar_vpn.py','preparar_continuidad.py','respaldos.py','configurar_https.py']:
        result=subprocess.run(['/usr/bin/python3',str(op.ROOT/'integracion'/script)],cwd=op.ROOT,timeout=600)
        if result.returncode:raise RuntimeError('No terminó '+script)
    if op.config()['aws']['variables'].get('enable_supabase'):
        subprocess.run([sys.executable,str(op.ROOT/'integracion/desplegar_supabase.py'),'--ejecutar'],cwd=op.ROOT,check=True,timeout=1200)
    from prueba_failover import health
    gcp_url='http://'+op.state('gcp')['vm_ip']+'/health'
    local_gcp=health(gcp_url)
    for _ in range(12):
        a=health(op.state('aws')['url']+'/health')
        # Comprobación servidor-servidor, independiente del filtro web local.
        response=op.ssm(op.state('aws')['vpn_instance'],
                        'curl --fail --silent --max-time 8 '+gcp_url,timeout=30)
        g={'http':200,'datos':json.loads(response['out']),'origen':'gateway AWS'}
        if a.get('http')==200 and g.get('http')==200 and not a['datos']['database']['recovery'] and g['datos']['database']['recovery'] and a['datos']['database']['probe']==g['datos']['database']['probe']:
            break
        time.sleep(2)
    else:raise RuntimeError('Las sondas no confirmaron roles y marcador coincidentes')
    evidence={'utc':datetime.now(timezone.utc).isoformat(),'aws':a,'gcp':g,'acceso_gcp_desde_equipo_local':local_gcp,'identificadores':{'db_aws':op.state('aws')['db_instance'],'volumen_aws':op.state('aws')['db_volume'],'vm_gcp':op.state('gcp')['vm_id'],'disco_gcp':op.state('gcp')['data_disk']},'completo':True}
    (op.ROOT/'integracion/evidencias/20261104/reencendido.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    print('Continuidad preparada. Verifica las sondas /health; el portal GCP tiene URL alternativa manual.')


if __name__=='__main__':main()
