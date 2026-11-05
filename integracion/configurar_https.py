#!/usr/bin/env python3
"""TLS académico del ALB: certificado propio, sin comprar dominio ni fingir confianza pública."""
from datetime import datetime,timezone
import argparse
import json
import re
import subprocess
import time
from urllib.parse import urlparse
import operaciones as op


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--ruta',default='/health',choices=['/','/health','/auth/v1/health'])
    options=parser.parse_args()
    op.assert_aws_identity();cfg=op.config();host=urlparse(op.state('aws')['url']).hostname
    if not host or not re.fullmatch(r'[a-zA-Z0-9.-]+',host) or not host.endswith('.elb.amazonaws.com'):
        raise RuntimeError('Nombre del ALB inesperado')
    folder=op.PRIVATE/'tls';folder.mkdir(mode=0o700,exist_ok=True)
    key=folder/'alb.key';cert=folder/'alb.crt'
    result=subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','30','-subj','/CN='+host,'-addext','subjectAltName=DNS:'+host,'-keyout',str(key),'-out',str(cert)],capture_output=True,text=True)
    if result.returncode:raise RuntimeError('No se pudo generar el certificado local')
    key.chmod(0o600);cert.chmod(0o600)
    args=['acm','import-certificate','--certificate','fileb://'+str(cert),'--private-key','fileb://'+str(key)]
    arn=cfg['aws']['variables'].get('certificate_arn','')
    if arn:
        tags=op.aws(['acm','list-tags-for-certificate','--certificate-arn',arn])['Tags']
        if not any(t['Key']=='proyecto' and t['Value']=='nexoandes' for t in tags):
            raise RuntimeError('No se reemplaza un certificado ajeno al flujo NexoAndes')
        args+=['--certificate-arn',arn]
    else:args+=['--tags','Key=proyecto,Value=nexoandes','Key=entorno,Value=academico']
    arn=op.aws(args)['CertificateArn'];cfg['aws']['variables']['certificate_arn']=arn
    op.control.save_json(op.control.CONFIG,cfg)
    log=op.PRIVATE/'https-aplicar.log'
    with log.open('w') as stream:
        log.chmod(0o600)
        result=subprocess.run([str(op.ROOT/'nexoandes'),'encender','--nube','aws'],cwd=op.ROOT,stdout=stream,stderr=subprocess.STDOUT,timeout=600)
    if result.returncode:raise RuntimeError('Revisar el apply privado de HTTPS')
    url='https://'+host+options.ruta
    deadline=time.monotonic()+120
    while True:
        check=subprocess.run(['curl','--cacert',str(cert),'--fail','--silent','--show-error','--max-time','10','--output','/dev/null','--write-out','%{http_code} %{ssl_verify_result}',url],capture_output=True,text=True,timeout=15)
        if check.returncode==0 or time.monotonic()>=deadline:break
        time.sleep(3)
    evidence={'utc':datetime.now(timezone.utc).isoformat(),'url':url,'http_y_verificacion':check.stdout,'correcto':check.returncode==0,'certificado':'autofirmado académico, 30 días; no confiable públicamente','verificacion':'curl verifica nombre y certificado con --cacert; no usa -k','http_80':'permanece habilitado para las pruebas existentes; riesgo residual'}
    (op.ROOT/'integracion/evidencias/20261104/https.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    if check.returncode:raise RuntimeError('No se validó HTTPS; revisar evidencia y listener')
    print(json.dumps(evidence,ensure_ascii=False))


if __name__=='__main__':main()
