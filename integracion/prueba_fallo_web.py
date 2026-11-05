#!/usr/bin/env python3
"""Terminar una web del ASG, medir HTTP y comprobar su reposición real."""
from datetime import datetime,timezone
import json
import threading
import time
import urllib.request
import operaciones as op
from preparar_continuidad import web_instances


def main():
    op.assert_aws_identity()
    op.aws(['autoscaling','suspend-processes','--auto-scaling-group-name','nexoandes-web','--scaling-processes','AlarmNotification'])
    op.aws(['autoscaling','set-desired-capacity','--auto-scaling-group-name','nexoandes-web','--desired-capacity','2','--no-honor-cooldown'])
    for _ in range(30):
        initial=web_instances()
        if len(initial)==2:break
        time.sleep(3)
    else:raise RuntimeError('El ASG no retornó a dos instancias')
    result={'utc':datetime.now(timezone.utc).isoformat(),'instancias_iniciales':initial,'tipo_fallo':'terminación controlada de una instancia web descartable','http':[]}
    url=op.state('aws')['url']+'/'
    stop=threading.Event()
    def poll():
        while not stop.is_set():
            try:
                request=urllib.request.Request(url+'?prueba_fallo='+str(time.time_ns()),headers={'Cache-Control':'no-cache'})
                with urllib.request.urlopen(request,timeout=5) as response:code=response.status;response.read()
            except Exception as error:code=getattr(error,'code',0)
            result['http'].append({'utc':datetime.now(timezone.utc).isoformat(),'codigo':code})
            stop.wait(1)
    thread=threading.Thread(target=poll,daemon=True);thread.start();started=time.monotonic()
    try:
        op.aws(['autoscaling','terminate-instance-in-auto-scaling-group','--instance-id',initial[0],'--no-should-decrement-desired-capacity'])
        for _ in range(90):
            current=web_instances()
            if len(current)==2 and initial[0] not in current:
                target=op.aws(['elbv2','describe-target-health','--target-group-arn',op.state('aws')['target_group']])
                healthy=[t for t in target['TargetHealthDescriptions'] if t['TargetHealth']['State']=='healthy']
                if len(healthy)==2:
                    result['repuesto']=True;result['instancias_finales']=current;break
            time.sleep(3)
        else:result['repuesto']=False
    finally:
        stop.set();thread.join(timeout=6)
        result['segundos_hasta_dos_saludables']=round(time.monotonic()-started,2)
        result['http_200']=sum(x['codigo']==200 for x in result['http'])
        result['http_errores']=sum(x['codigo']!=200 for x in result['http'])
        op.aws(['autoscaling','resume-processes','--auto-scaling-group-name','nexoandes-web','--scaling-processes','AlarmNotification'])
        result['nota']='AlarmNotification se suspendió para aislar el ensayo y se reanuda al terminar.'
        (op.ROOT/'integracion/evidencias/20261104/fallo-web.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='http'},ensure_ascii=False))


if __name__=='__main__':main()
