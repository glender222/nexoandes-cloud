#!/usr/bin/env python3
"""Primitivas administrativas acotadas; parámetros sensibles quedan en privado."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT/'integracion/privado'
PRIVATE.mkdir(mode=0o700, exist_ok=True)
PRIVATE.chmod(0o700)
spec=importlib.util.spec_from_file_location('nexo_control',ROOT/'infraestructura/control.py')
control=importlib.util.module_from_spec(spec);spec.loader.exec_module(control)

def config():
    return json.loads(control.CONFIG.read_text())

def aws(args, *, timeout=75):
    settings=config()['aws'];env,_=control.cloud_environment('aws',settings)
    env['AWS_MAX_ATTEMPTS']='2'
    result=subprocess.run(['aws',*args,'--region',settings['region'],'--output','json'],env=env,capture_output=True,text=True,timeout=timeout)
    if result.returncode:
        raise RuntimeError(result.stderr.strip()[:1600])
    return json.loads(result.stdout) if result.stdout.strip() else None

def assert_aws_identity():
    identity=aws(['sts','get-caller-identity'])
    if identity['Account']!=config()['aws']['cuenta']:
        raise RuntimeError('Cuenta AWS inesperada')

def state(cloud):
    settings=config()[cloud]
    return json.loads(control.state_path(cloud,settings).read_text())['outputs']['control']['value']

def ssm(instance, script, *, timeout=240):
    if not script.startswith('#!'):
        script = '#!/bin/bash\n'+script
    payload={'DocumentName':'AWS-RunShellScript','InstanceIds':[instance],
             'Parameters':{'commands':[script],'executionTimeout':[str(timeout)]},
             'Comment':'NexoAndes V2: operacion autorizada y acotada'}
    fd,name=tempfile.mkstemp(prefix='ssm-',suffix='.json',dir=PRIVATE)
    try:
        with os.fdopen(fd,'w') as stream:json.dump(payload,stream)
        command=aws(['ssm','send-command','--cli-input-json','file://'+name])['Command']['CommandId']
    finally:
        Path(name).unlink(missing_ok=True)
    deadline=time.monotonic()+timeout+45
    while time.monotonic()<deadline:
        try:result=aws(['ssm','get-command-invocation','--command-id',command,'--instance-id',instance])
        except RuntimeError as error:
            if 'InvocationDoesNotExist' in str(error):time.sleep(2);continue
            raise
        if result['Status'] not in ['Pending','InProgress','Delayed']:
            if result['Status']!='Success':
                # Los scripts no deben imprimir secretos. La salida completa queda privada.
                path=PRIVATE/(command+'-fallo.json');path.write_text(json.dumps(result));path.chmod(0o600)
                raise RuntimeError(f"SSM {command}: {result['Status']}; detalle privado {path}")
            return {'command_id':command,'status':result['Status'],'out':result.get('StandardOutputContent','').strip()}
        time.sleep(2)
    raise TimeoutError('SSM no finalizó dentro del tiempo acotado')

def ssh(script, *, timeout=120):
    host=state('gcp')['vm_ip']
    if config()['gcp'].get('via_gateway'):
        import base64, shlex
        content=base64.b64encode(script.encode()).decode()
        invocation=f"printf '%s' {shlex.quote(content)} | base64 -d | ssh -i /root/.ssh/nexoandes-gcp -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 -o BatchMode=yes nexoandes@{host} sudo bash -s"
        return ssm(state('aws')['vpn_instance'],invocation,timeout=timeout)['out']
    args=['ssh','-i',str(PRIVATE/'gcp-admin'),'-o','StrictHostKeyChecking=accept-new','-o','UserKnownHostsFile='+str(PRIVATE/'known_hosts'),'-o','ConnectTimeout=10','-o','BatchMode=yes','nexoandes@'+host,'sudo','bash','-s']
    result=subprocess.run(args,input=script,text=True,capture_output=True,timeout=timeout)
    if result.returncode:
        (PRIVATE/'ssh-ultimo-fallo.txt').write_text(result.stdout+'\n'+result.stderr)
        (PRIVATE/'ssh-ultimo-fallo.txt').chmod(0o600)
        raise RuntimeError('SSH falló; detalle en integracion/privado/ssh-ultimo-fallo.txt')
    return result.stdout.strip()

def private_settings():
    import secrets
    path=PRIVATE/'continuidad.json'
    if not path.exists():
        path.write_text(json.dumps({'ipsec_psk':secrets.token_hex(32),'replication_password':secrets.token_hex(24),'app_password':secrets.token_hex(24)},indent=2)+'\n')
        path.chmod(0o600)
    return json.loads(path.read_text())

def write_remote(path, content, *, mode='600'):
    import base64,shlex
    encoded=base64.b64encode(content.encode()).decode()
    return f"mkdir -p {shlex.quote(str(Path(path).parent))}\nprintf '%s' {shlex.quote(encoded)} | base64 -d > {shlex.quote(path)}\nchmod {mode} {shlex.quote(path)}\n"
