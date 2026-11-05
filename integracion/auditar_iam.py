#!/usr/bin/env python3
"""Inventario IAM de lectura; no exporta claves. API de proyecto GCP opcional."""
import argparse
from pathlib import Path
from datetime import datetime,timezone
import sys,json,subprocess,concurrent.futures
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'integracion'));import operaciones as op
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--politica-proyecto',action='store_true',help='Requiere Cloud Resource Manager API habilitada');args=parser.parse_args()
cfg=op.config();out={'utc':datetime.now(timezone.utc).isoformat(),'modo':'lectura','nubes':{}}
def aws():
 op.assert_aws_identity();a={'identidad':op.aws(['sts','get-caller-identity'])}
 def call(args):
  try:return {'ok':True,'datos':op.aws(args)}
  except RuntimeError as e:return {'ok':False,'error':str(e)[:900]}
 cmds={'rol': ['iam','get-role','--role-name','LabRole'],'perfil':['iam','get-instance-profile','--instance-profile-name','LabInstanceProfile'],'adjuntas':['iam','list-attached-role-policies','--role-name','LabRole'],'inline':['iam','list-role-policies','--role-name','LabRole'],'instancias':['ec2','describe-instances','--filters','Name=tag:Name,Values=nexoandes-*','--query','Reservations[].Instances[?State.Name!=`terminated`].{id:InstanceId,nombre:Tags[?Key==`Name`].Value|[0],perfil:IamInstanceProfile.Arn,estado:State.Name,imds:MetadataOptions.HttpTokens}[]']}
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
  fs={ex.submit(call,c):k for k,c in cmds.items()}
  for f in concurrent.futures.as_completed(fs):a[fs[f]]=f.result()
 a['politicas']={}
 if a['inline']['ok']:
  for n in a['inline']['datos']['PolicyNames']:a['politicas'][n]=call(['iam','get-role-policy','--role-name','LabRole','--policy-name',n])
 if a['adjuntas']['ok']:
  for p in a['adjuntas']['datos']['AttachedPolicies']:
   m=call(['iam','get-policy','--policy-arn',p['PolicyArn']])
   a['politicas'][p['PolicyName']]=call(['iam','get-policy-version','--policy-arn',p['PolicyArn'],'--version-id',m['datos']['Policy']['DefaultVersionId']]) if m['ok'] else m
 return a

def azcall(args):
 env,_=op.control.cloud_environment('azure',cfg['azure']);r=subprocess.run(['az',*args,'--output','json'],env=env,capture_output=True,text=True,timeout=65)
 return {'ok':r.returncode==0,'datos':json.loads(r.stdout or 'null') if not r.returncode else None,'error':r.stderr.strip()[:900] if r.returncode else None}
def azure():
 c=cfg['azure'];sub=c['suscripcion'];scope=f'/subscriptions/{sub}/resourceGroups/nexoandes-lab/providers/Microsoft.Storage/storageAccounts/{c["variables"]["storage_account_name"]}'
 ident=azcall(['account','show','--subscription',sub,'--query','{suscripcion:id,tenant:tenantId,tipo:user.type}']);assert ident['ok'] and ident['datos']['suscripcion']==sub and ident['datos']['tenant']==c['tenant']
 who=azcall(['ad','signed-in-user','show','--query','{object_id:id}'])
 args=['role','assignment','list','--scope',scope+'/blobServices/default/containers/postgresql','--include-inherited','--fill-principal-name','false','--query','[].{nombre:roleDefinitionName,scope:scope,principal:principalId,tipo:principalType,id:id}']
 if who['ok']:args+=['--assignee-object-id',who['datos']['object_id']]
 return {'identidad':ident,'principal':who,'scope_storage':scope,'scope_contenedor':scope+'/blobServices/default/containers/postgresql','asignaciones':azcall(args),'acceso_entra':azcall(['storage','blob','list','--account-name',c['variables']['storage_account_name'],'--container-name','postgresql','--auth-mode','login','--only-show-errors','--num-results','2','--query','[].{nombre:name,bytes:properties.contentLength}'])}
def gcp():
 from google.oauth2 import service_account
 from google.auth.transport.requests import AuthorizedSession
 c=cfg['gcp'];k=Path(c['service_account_key']);k=k if k.is_absolute() else ROOT/k
 cr=service_account.Credentials.from_service_account_file(str(k),scopes=['https://www.googleapis.com/auth/cloud-platform']);assert cr.project_id==c['proyecto'];s=AuthorizedSession(cr);p=c['proyecto'];member='serviceAccount:'+cr.service_account_email
 def req(method,url,body=None):
  r=s.request(method,url,json=body,timeout=35);return {'ok':r.ok,'http':r.status_code,'datos':r.json() if r.ok else None,'error':r.json().get('error',{}).get('message') if not r.ok else None}
 pol=req('POST',f'https://cloudresourcemanager.googleapis.com/v1/projects/{p}:getIamPolicy',{'options':{'requestedPolicyVersion':3}}) if args.politica_proyecto else {'ok':False,'omitida':'Consulta global opcional; véase INC-031. Los permisos de Storage se verifican abajo.'}
 if pol['ok']:pol['datos']={'version':pol['datos'].get('version'),'roles_principal':[{'role':b['role'],'condition':b.get('condition')} for b in pol['datos'].get('bindings',[]) if member in b['members']]}
 b=op.state('gcp')['bucket']
 return {'identidad':{'proyecto':p,'cuenta_servicio':cr.service_account_email},'politica_proyecto':pol,'politica_bucket':req('GET',f'https://storage.googleapis.com/storage/v1/b/{b}/iam'),'permisos_bucket':req('GET',f'https://storage.googleapis.com/storage/v1/b/{b}/iam/testPermissions?permissions=storage.objects.list&permissions=storage.objects.get&permissions=storage.objects.create&permissions=storage.objects.delete&permissions=storage.buckets.get&permissions=storage.buckets.getIamPolicy'),'vm':req('GET',f'https://compute.googleapis.com/compute/v1/projects/{p}/zones/us-central1-a/instances/nexoandes-gcp-standby?fields=name,status,serviceAccounts')}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 fs={ex.submit(fn):n for n,fn in [('aws',aws),('azure',azure),('gcp',gcp)]}
 for f in concurrent.futures.as_completed(fs):
  n=fs[f]
  try:out['nubes'][n]=f.result();print(n,'auditado',flush=True)
  except Exception as e:out['nubes'][n]={'error':str(e)[:900]};print(n,'consulta fallida',flush=True)
path=ROOT/'integracion/evidencias'/datetime.now(timezone.utc).strftime('%Y%m%d')/'iam'/('inventario-'+datetime.now(timezone.utc).strftime('%H%M%SZ')+'.json');path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(path)
