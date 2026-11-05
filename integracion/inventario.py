#!/usr/bin/env python3
"""Inventario de lectura con identidades fijadas y salidas sin credenciales."""
import argparse
import concurrent.futures
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('nexo_control', ROOT/'infraestructura/control.py')
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)

def cli(args, env):
    result = subprocess.run(args, env=env, capture_output=True, text=True, timeout=65)
    if result.returncode:
        return {'ok':False, 'error':result.stderr.strip()[:1800]}
    return {'ok':True, 'datos':json.loads(result.stdout or 'null')}

def inventory_aws(config):
    settings=config['aws']; env,_=control.cloud_environment('aws',settings)
    env['AWS_MAX_ATTEMPTS']='1'
    prefix=['aws','--region',settings['region'],'--output','json','--cli-connect-timeout','10','--cli-read-timeout','30']
    identity=cli(prefix+['sts','get-caller-identity','--query','{Account:Account,Arn:Arn}'],env)
    if not identity['ok'] or identity['datos']['Account']!=settings['cuenta']:
        raise RuntimeError('AWS: no se confirmó la cuenta esperada')
    commands={
      'instancias':['ec2','describe-instances','--query','Reservations[].Instances[].{id:InstanceId,estado:State.Name,tipo:InstanceType,az:Placement.AvailabilityZone,ip_privada:PrivateIpAddress,ip_publica:PublicIpAddress,vpc:VpcId,subnet:SubnetId,nombre:Tags[?Key==`Name`].Value|[0]}'],
      'volumenes':['ec2','describe-volumes','--query','Volumes[].{id:VolumeId,estado:State,az:AvailabilityZone,gb:Size,cifrado:Encrypted,attachments:Attachments[].InstanceId}'],
      'vpcs':['ec2','describe-vpcs','--query','Vpcs[].{id:VpcId,cidr:CidrBlock,estado:State,nombre:Tags[?Key==`Name`].Value|[0]}'],
      'subnets':['ec2','describe-subnets','--query','Subnets[].{id:SubnetId,vpc:VpcId,cidr:CidrBlock,az:AvailabilityZone}'],
      'alb':['elbv2','describe-load-balancers','--query','LoadBalancers[].{nombre:LoadBalancerName,arn:LoadBalancerArn,dns:DNSName,estado:State.Code,az:AvailabilityZones[].ZoneName}'],
      'asg':['autoscaling','describe-auto-scaling-groups','--query','AutoScalingGroups[].{nombre:AutoScalingGroupName,min:MinSize,max:MaxSize,deseado:DesiredCapacity,health:HealthCheckType,instancias:Instances[].{id:InstanceId,estado:HealthStatus,az:AvailabilityZone}}'],
      'nat':['ec2','describe-nat-gateways','--query','NatGateways[].{id:NatGatewayId,estado:State,subnet:SubnetId}'],
      'ssm':['ssm','describe-instance-information','--query','InstanceInformationList[].{id:InstanceId,estado:PingStatus,plataforma:PlatformName}'],
      'alarmas':['cloudwatch','describe-alarms','--query','MetricAlarms[].{nombre:AlarmName,estado:StateValue,metrica:MetricName,acciones:AlarmActions}'],
      's3':['s3api','list-objects-v2','--bucket',f"nexoandes-backup-{settings['cuenta']}-{settings['region']}",'--query','{cantidad:KeyCount,objetos:Contents[].{clave:Key,bytes:Size,fecha:LastModified}}'],
      'vpn':['ec2','describe-vpn-connections','--query','VpnConnections[].{id:VpnConnectionId,estado:State}'],
      'costos':['ce','get-cost-and-usage','--time-period','Start=2026-11-01,End=2026-11-05','--granularity','MONTHLY','--metrics','UnblendedCost','--query','ResultsByTime[].{periodo:TimePeriod,total:Total.UnblendedCost,estimado:Estimated}'],
    }
    output={'identidad':identity,'region':settings['region']}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        tasks={pool.submit(cli,prefix+args,env):name for name,args in commands.items()}
        for task in concurrent.futures.as_completed(tasks): output[tasks[task]]=task.result()
    return output

def inventory_azure(config):
    settings=config['azure']; env,_=control.cloud_environment('azure',settings)
    subscription=settings['suscripcion']
    commands={
      'identidad':['az','rest','--method','get','--url',f'https://management.azure.com/subscriptions/{subscription}?api-version=2022-12-01','--query','{id:subscriptionId,nombre:displayName,estado:state}'],
      'recursos':['az','resource','list','--subscription',subscription,'--query','[].{id:id,nombre:name,tipo:type,grupo:resourceGroup,region:location}'],
      'maquinas':['az','vm','list','--show-details','--subscription',subscription,'--query','[].{nombre:name,grupo:resourceGroup,region:location,estado:powerState,tipo:hardwareProfile.vmSize}'],
      'regiones':['az','policy','assignment','list','--subscription',subscription,'--query','[?contains(displayName, `region`)].{nombre:displayName,parametros:parameters}'],
      'costos':['az','rest','--method','post','--url',f'https://management.azure.com/subscriptions/{subscription}/providers/Microsoft.CostManagement/query?api-version=2023-11-01','--body',json.dumps({'type':'ActualCost','timeframe':'MonthToDate','dataset':{'granularity':'None','aggregation':{'totalCost':{'name':'Cost','function':'Sum'}}}}),'--query','properties.{columnas:columns,filas:rows}'],
    }
    output={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        tasks={pool.submit(cli,args+['--output','json'],env):name for name,args in commands.items()}
        for task in concurrent.futures.as_completed(tasks): output[tasks[task]]=task.result()
    return output

def inventory_gcp(config):
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession
    settings=config['gcp']; project=settings['proyecto']
    key=Path(settings['service_account_key']);key=key if key.is_absolute() else ROOT/key
    creds=service_account.Credentials.from_service_account_file(str(key),scopes=['https://www.googleapis.com/auth/cloud-platform'])
    if creds.project_id!=project: raise RuntimeError('GCP: proyecto inesperado')
    session=AuthorizedSession(creds)
    def get(url):
        response=session.get(url,timeout=35); data=response.json()
        return {'ok':response.ok,'http':response.status_code,'datos':data} if response.ok else {'ok':False,'http':response.status_code,'error':data.get('error',{}).get('message','Error sin mensaje')}
    output={'identidad':{'proyecto':project,'cuenta_servicio':creds.service_account_email},'region':settings['region']}
    for name,url in {
      'instancias':f'https://compute.googleapis.com/compute/v1/projects/{project}/aggregated/instances?returnPartialSuccess=true',
      'discos':f'https://compute.googleapis.com/compute/v1/projects/{project}/aggregated/disks?returnPartialSuccess=true',
      'redes':f'https://compute.googleapis.com/compute/v1/projects/{project}/global/networks',
      'firewalls':f'https://compute.googleapis.com/compute/v1/projects/{project}/global/firewalls',
      'buckets':f'https://storage.googleapis.com/storage/v1/b?project={project}&fields=items(name,location,versioning,lifecycle)',
      'objetos':f'https://storage.googleapis.com/storage/v1/b/nexoandes-backup-{project}/o?fields=items(name,size,updated)',
      'facturacion':f'https://cloudbilling.googleapis.com/v1/projects/{project}/billingInfo',
    }.items():
        result=get(url)
        if result['ok'] and name in ['instancias','discos']:
            flattened=[]
            for scope,group in result['datos'].get('items',{}).items():
                for item in group.get('instances' if name=='instancias' else 'disks',[]):
                    flattened.append({k:item[k] for k in ['id','name','status','zone','machineType','sizeGb','type','users','networkInterfaces','disks'] if k in item})
            result['datos']=flattened
        if result['ok'] and name in ['redes','firewalls']:
            fields=['name','network','sourceRanges','allowed','targetTags','routingConfig','subnetworks','autoCreateSubnetworks','selfLink','direction']
            result['datos']=[{k:item[k] for k in fields if k in item} for item in result['datos'].get('items',[])]
        output[name]=result
    return output

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--salida',type=Path,required=True);args=parser.parse_args()
    config=json.loads(control.CONFIG.read_text());output={'utc':datetime.now(timezone.utc).isoformat(),'solo_lectura':True,'nubes':{}}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        tasks={pool.submit(fn,config):name for name,fn in [('aws',inventory_aws),('azure',inventory_azure),('gcp',inventory_gcp)]}
        for task in concurrent.futures.as_completed(tasks):
            name=tasks[task]
            try: output['nubes'][name]=task.result();print(name+': inventario obtenido',flush=True)
            except Exception as error: output['nubes'][name]={'error':str(error)[:1000]};print(name+': consulta fallida',flush=True)
    args.salida.parent.mkdir(parents=True,exist_ok=True)
    args.salida.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
