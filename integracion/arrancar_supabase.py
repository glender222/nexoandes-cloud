#!/usr/bin/env python3
"""Reproducir Supabase AWS, TLS y acceso web sin arrancar computo Azure/GCP."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
import tarfile
import operaciones as op
from desplegar_supabase import preparer
from arrancar_continuidad import apply


def main():
    argparse.ArgumentParser(description='Iniciar Supabase autohospedado e integrar Auth en NexoAndes').parse_args()
    op.assert_aws_identity()
    settings=preparer.prepare('https://localhost')
    archive=preparer.PRIVATE/'web-auth.tgz'
    with tarfile.open(archive,'w:gz') as stream:
        for name in ['instalar_web.py','portal_backend.py','acceso.html','acceso.js','estilo.css']:
            stream.add(Path(__file__).parent/'supabase'/name,arcname=name)
    archive.chmod(0o600);digest=hashlib.sha256(archive.read_bytes()).hexdigest();key='supabase-web/'+digest+'.tgz'
    op.aws(['s3api','put-object','--bucket',op.state('aws')['bucket'],'--key',key,'--body',str(archive),'--server-side-encryption','AES256'])
    config=op.config();config['aws']['variables'].update(enable_supabase=True,supabase_web_key=key,supabase_web_sha256=digest,supabase_publishable_key=settings['SUPABASE_PUBLISHABLE_KEY'])
    op.control.save_json(op.control.CONFIG,config)
    apply('aws')
    commands=[['configurar_https.py','--ruta','/'],['desplegar_supabase.py','--ejecutar'],['supabase/verificar.py'],['respaldos.py','--tipo','supabase','--generar']]
    for command in commands:
        subprocess.run([sys.executable,str(op.ROOT/'integracion'/command[0]),*command[1:]],cwd=op.ROOT,check=True,timeout=1200)
    print('Supabase y Auth verificados. Acceso:',op.state('aws')['https_url']+'/acceso/')


if __name__=='__main__':main()
