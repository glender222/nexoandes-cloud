#!/usr/bin/env python3
"""Copiar el último dump S3 a Azure/GCP, descargarlo y contrastar SHA256."""
import argparse
import fcntl
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
from urllib.parse import quote
import operaciones as op


def azure(args,env):
    p=subprocess.run(['az',*args,'--output','json'],env=env,capture_output=True,text=True,timeout=90)
    if p.returncode:raise RuntimeError('Azure: '+p.stderr[:1400])
    return json.loads(p.stdout) if p.stdout.strip() else None


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--generar',action='store_true')
    parser.add_argument('--tipo',choices=['postgresql','supabase'],default='postgresql');args=parser.parse_args()
    op.assert_aws_identity();aws=op.state('aws');cfg=op.config();folder=op.PRIVATE/'respaldos'
    folder.mkdir(mode=0o700,exist_ok=True)
    if args.generar:
        target=aws['db_instance'] if args.tipo=='postgresql' else aws['supabase_instance']
        command='/usr/local/sbin/nexoandes-backup' if args.tipo=='postgresql' else '/usr/local/sbin/nexoandes-supabase-backup'
        op.ssm(target,'set -e; '+command,timeout=180)
    objects=op.aws(['s3api','list-objects-v2','--bucket',aws['bucket'],'--prefix',args.tipo+'/']).get('Contents',[])
    objects=[o for o in objects if o['Key'].endswith('.dump' if args.tipo=='postgresql' else '.tgz')]
    if not objects:raise RuntimeError('No hay respaldos del tipo solicitado; no se generaron copias ficticias')
    last=max(objects,key=lambda o:o['LastModified']);key=last['Key']
    local=folder/Path(key).name
    op.aws(['s3api','get-object','--bucket',aws['bucket'],'--key',key,str(local)])
    local.chmod(0o600);original=local.read_bytes();digest=hashlib.sha256(original).hexdigest()
    env,_=op.control.cloud_environment('azure',cfg['azure'])
    account=cfg['azure']['variables']['storage_account_name']
    # El usuario Entra requiere Storage Blob Data Contributor en este contenedor.
    env={k:v for k,v in env.items() if k not in ('AZURE_STORAGE_KEY','AZURE_STORAGE_CONNECTION_STRING','AZURE_STORAGE_SAS_TOKEN')}
    env['AZURE_STORAGE_ACCOUNT']=account
    azure(['storage','blob','upload','--container-name','postgresql','--name',key,'--file',str(local),'--overwrite','true','--auth-mode','login','--only-show-errors'],env)
    azure_download=folder/(local.name+'.azure')
    azure(['storage','blob','download','--container-name','postgresql','--name',key,'--file',str(azure_download),'--overwrite','true','--auth-mode','login','--only-show-errors'],env)
    azure_download.chmod(0o600)
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession
    gcp=cfg['gcp'];credential=Path(gcp['service_account_key']);credential=credential if credential.is_absolute() else op.ROOT/credential
    creds=service_account.Credentials.from_service_account_file(str(credential),scopes=['https://www.googleapis.com/auth/devstorage.read_write'])
    if creds.project_id!=gcp['proyecto']:raise RuntimeError('Proyecto GCP inesperado')
    session=AuthorizedSession(creds);bucket=op.state('gcp')['bucket']
    response=session.post(f'https://storage.googleapis.com/upload/storage/v1/b/{bucket}/o?uploadType=media&name={quote(key,safe="")}',data=original,headers={'Content-Type':'application/octet-stream'},timeout=60)
    response.raise_for_status()
    response=session.get(f'https://storage.googleapis.com/storage/v1/b/{bucket}/o/{quote(key,safe="")}?alt=media',timeout=60)
    response.raise_for_status();gcp_download=folder/(local.name+'.gcp');gcp_download.write_bytes(response.content);gcp_download.chmod(0o600)
    hashes={'aws':digest,'azure':hashlib.sha256(azure_download.read_bytes()).hexdigest(),'gcp':hashlib.sha256(response.content).hexdigest()}
    result={'utc':datetime.now(timezone.utc).isoformat(),'objeto':key,'bytes':len(original),'sha256':hashes,'coinciden':len(set(hashes.values()))==1,
            'mecanismo':'S3 API; Azure Blob HTTPS y Google Cloud Storage HTTPS autenticados; sin VPN para objetos',
            'azure_autenticacion':'Microsoft Entra ID/RBAC --auth-mode login; sin claves de almacenamiento',
            'ejecutor':'equipo local; requiere equipo encendido y credenciales vigentes','generacion_solicitada':args.generar,'restauracion':'se acredita por separado'}
    if not result['coinciden']:raise RuntimeError('Las copias descargadas no coinciden')
    dest=op.ROOT/'integracion/evidencias'/datetime.now(timezone.utc).strftime('%Y%m%d')/('respaldos.json' if args.tipo=='postgresql' else 'supabase/respaldos.json')
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':
    with (op.PRIVATE/'respaldos.lock').open('a') as lock:
        try:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            print('Otra copia NexoAndes está en curso; esta ejecución no la duplica.')
            raise SystemExit(0)
        main()
