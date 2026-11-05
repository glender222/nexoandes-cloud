#!/usr/bin/env python3
"""Carga acotada: medir crecimiento real del ASG y retirar carga al terminar."""
from datetime import datetime, timezone
import concurrent.futures
import json
import time
import operaciones as op
from preparar_continuidad import web_instances


def group():
    return op.aws(['autoscaling','describe-auto-scaling-groups','--auto-scaling-group-names','nexoandes-web'])['AutoScalingGroups'][0]


def main():
    op.assert_aws_identity();initial=web_instances()
    if len(initial)!=2:raise RuntimeError('La prueba requiere exactamente dos destinos iniciales')
    op.aws(['ec2','monitor-instances','--instance-ids',*initial])
    result={'utc':datetime.now(timezone.utc).isoformat(),'inicial':initial,'muestras':[],'carga_limitada_segundos':480}
    command='set -e; systemd-run --unit=nexoandes-carga --property=RuntimeMaxSec=480 /bin/bash -c "for cpu in 1 2; do (while :; do :; done) & done; wait"; echo CARGA_INICIADA'
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda i:op.ssm(i,command,timeout=40),initial))
    start=time.monotonic();scaled=False
    try:
        while time.monotonic()-start<600:
            data=group();entry={'segundos':round(time.monotonic()-start,1),'deseado':data['DesiredCapacity'],'instancias':[{k:i[k] for k in ['InstanceId','LifecycleState','HealthStatus']} for i in data['Instances']]}
            result['muestras'].append(entry)
            print('ASG:',entry['deseado'],'deseadas;',len(entry['instancias']),'instancias;',entry['segundos'],'s',flush=True)
            if data['DesiredCapacity']>2:
                scaled=True
                if len([i for i in data['Instances'] if i['LifecycleState']=='InService'])>=data['DesiredCapacity']:break
            time.sleep(25)
    finally:
        for instance in initial:
            try:op.ssm(instance,'systemctl stop nexoandes-carga || true; echo CARGA_RETIRADA',timeout=35)
            except Exception:pass
    result['aumento_automatico_observado']=scaled
    result['actividades']=op.aws(['autoscaling','describe-scaling-activities','--auto-scaling-group-name','nexoandes-web','--max-items','8','--query','Activities[].{fecha:StartTime,estado:StatusCode,causa:Cause,descripcion:Description}'])
    result['alarmas']=op.aws(['cloudwatch','describe-alarms','--query','MetricAlarms[?contains(AlarmName, `nexoandes`)].{nombre:AlarmName,estado:StateValue,metrica:MetricName}'])
    path=op.ROOT/'integracion/evidencias/20261104/escalabilidad.json';path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    # Restablecer la capacidad de laboratorio; no se presenta como escala-in automático.
    op.aws(['autoscaling','set-desired-capacity','--auto-scaling-group-name','nexoandes-web','--desired-capacity','2','--no-honor-cooldown'])
    print('Resultado crecimiento automático:',scaled,'; capacidad deseada restablecida manualmente a 2.')


if __name__=='__main__':main()
