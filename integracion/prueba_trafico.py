#!/usr/bin/env python3
"""Generar tráfico HTTP acotado y medir scale-out real por solicitudes."""
from datetime import datetime, timezone
import json
import threading
import time
import urllib.request
import operaciones as op
from preparar_continuidad import web_instances


def main():
    op.assert_aws_identity();initial=web_instances()
    if len(initial)!=2:raise RuntimeError('La prueba requiere dos instancias iniciales')
    url=op.state('aws')['url']+'/'
    stop=threading.Event();lock=threading.Lock();counts={'ok':0,'errores':0}
    def worker():
        while not stop.is_set():
            try:
                with urllib.request.urlopen(url,timeout=3) as response:
                    response.read();valid=response.status==200
            except Exception:valid=False
            with lock:counts['ok' if valid else 'errores']+=1
            stop.wait(0.5)
    threads=[threading.Thread(target=worker,daemon=True) for _ in range(4)]
    result={'utc':datetime.now(timezone.utc).isoformat(),'metrica':'ALBRequestCountPerTarget','objetivo_por_destino_minuto':30,'umbral_de_demostracion':True,'inicial':initial,'muestras':[]}
    for thread in threads:thread.start()
    start=time.monotonic();scaled=False
    try:
        while time.monotonic()-start<600:
            data=op.aws(['autoscaling','describe-auto-scaling-groups','--auto-scaling-group-names','nexoandes-web'])['AutoScalingGroups'][0]
            entry={'segundos':round(time.monotonic()-start,1),'deseado':data['DesiredCapacity'],'instancias':[{k:i[k] for k in ['InstanceId','LifecycleState','HealthStatus']} for i in data['Instances']]}
            result['muestras'].append(entry)
            print('ASG:',entry['deseado'],'deseadas;',len(entry['instancias']),'instancias;',entry['segundos'],'s',flush=True)
            if data['DesiredCapacity']>2:
                scaled=True
                if len([i for i in data['Instances'] if i['LifecycleState']=='InService'])>=data['DesiredCapacity']:break
            time.sleep(25)
    finally:
        stop.set()
        for thread in threads:thread.join(timeout=4)
        result['http']=counts;result['aumento_automatico_observado']=scaled
        result['actividades']=op.aws(['autoscaling','describe-scaling-activities','--auto-scaling-group-name','nexoandes-web','--max-items','8','--query','Activities[].{fecha:StartTime,estado:StatusCode,causa:Cause,descripcion:Description}'])
        result['alarmas']=op.aws(['cloudwatch','describe-alarms','--query','MetricAlarms[?contains(AlarmName, `nexoandes`)].{nombre:AlarmName,estado:StateValue,metrica:MetricName}'])
        (op.ROOT/'integracion/evidencias/20261104/escalabilidad.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        op.aws(['autoscaling','set-desired-capacity','--auto-scaling-group-name','nexoandes-web','--desired-capacity','2','--no-honor-cooldown'])
    print('Scale-out automático observado:',scaled,'; retorno a capacidad 2 solicitado manualmente.')


if __name__=='__main__':main()
