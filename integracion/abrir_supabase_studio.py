#!/usr/bin/env python3
"""Abrir Studio por un tunel local SSM, sin publicar el panel en Internet."""
import argparse
import os
import shutil
import operaciones as op


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--puerto',type=int,default=8800);args=parser.parse_args()
    if not 1024<=args.puerto<=65535:parser.error('El puerto local debe estar entre 1024 y 65535')
    op.assert_aws_identity();state=op.state('aws')
    env,_=op.control.cloud_environment('aws',op.config()['aws'])
    env['PATH']=str(op.ROOT/'infraestructura/privado/bin')+os.pathsep+env['PATH']
    if not shutil.which('session-manager-plugin',path=env['PATH']):
        raise RuntimeError('Instala el plugin oficial AWS Session Manager; ver integracion/SUPABASE.md')
    print(f'Studio: http://127.0.0.1:{args.puerto} — mantener esta terminal abierta. No se encienden recursos.',flush=True)
    params='{"portNumber":["8000"],"localPortNumber":["'+str(args.puerto)+'"]}'
    os.execvpe('aws',['aws','ssm','start-session','--region',op.config()['aws']['region'],'--target',state['supabase_instance'],'--document-name','AWS-StartPortForwardingSession','--parameters',params],env)


if __name__=='__main__':main()
