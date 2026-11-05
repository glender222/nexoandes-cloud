#!/usr/bin/env python3
"""Generar una pila fijada y secretos privados; no arranca recursos."""
from pathlib import Path
import json
import os
import secrets
import shutil
import subprocess
import copy
import hashlib
from urllib.request import urlopen
import yaml

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'integracion/supabase/upstream'
PRIVATE = ROOT/'integracion/privado/supabase'
STACK = PRIVATE/'stack'


def read_env(path):
    return dict(line.split('=',1) for line in path.read_text().splitlines()
                if line and not line.startswith('#') and '=' in line)


def prepare(url):
    os.umask(0o077)
    PRIVATE.mkdir(parents=True,exist_ok=True,mode=0o700)
    shutil.copytree(SOURCE,STACK,dirs_exist_ok=True)
    env=STACK/'.env'
    if not env.exists():
        example=PRIVATE/'upstream.env.example'
        if not example.exists():
            origin=json.loads((SOURCE.parent/'ORIGEN.json').read_text())
            with urlopen('https://raw.githubusercontent.com/supabase/supabase/'+origin['commit']+'/docker/.env.example',timeout=30) as response:content=response.read()
            if hashlib.sha256(content).hexdigest()!=origin['env_example_sha256']:raise RuntimeError('Plantilla upstream no coincide con la version fijada')
            example.write_bytes(content);example.chmod(0o600)
        shutil.copy(PRIVATE/'upstream.env.example',env)
        with (PRIVATE/'generacion-secretos.log').open('w') as log:
            subprocess.run(['sh','utils/generate-keys.sh','--update-env'],cwd=STACK,stdout=log,stderr=subprocess.STDOUT,check=True)
            subprocess.run(['sh','utils/add-new-auth-keys.sh','--update-env'],cwd=STACK,stdout=log,stderr=subprocess.STDOUT,check=True)
        settings=read_env(env)
        settings.update(POSTGRES_PASSWORD=secrets.token_hex(24),
                        DASHBOARD_PASSWORD=secrets.token_hex(24),DASHBOARD_USERNAME='nexoandes',
                        DISABLE_SIGNUP='true',ENABLE_EMAIL_SIGNUP='true',ENABLE_EMAIL_AUTOCONFIRM='false',
                        ENABLE_PHONE_SIGNUP='false',ENABLE_PHONE_AUTOCONFIRM='false',ENABLE_ANONYMOUS_USERS='false',
                        JWT_EXPIRY='300',SMTP_HOST='127.0.0.1',SMTP_PORT='2525',SMTP_USER='',SMTP_PASS='',
                        SMTP_ADMIN_EMAIL='noreply@example.invalid',SMTP_SENDER_NAME='NexoAndes',
                        OPENAI_API_KEY='',STUDIO_DEFAULT_ORGANIZATION='NexoAndes',STUDIO_DEFAULT_PROJECT='NexoAndes académico')
        demo={'email':'demo.nexoandes@example.invalid','password':secrets.token_urlsafe(24)}
        (PRIVATE/'acceso-demo.json').write_text(json.dumps(demo,indent=2)+'\n')
    else:
        settings=read_env(env)
    settings.update(PGRST_DB_SCHEMAS='public',SUPABASE_PUBLIC_URL=url,API_EXTERNAL_URL=url+'/auth/v1',
                    SITE_URL=url+'/acceso/',ADDITIONAL_REDIRECT_URLS=url+'/acceso/',COMPOSE_FILE='docker-compose.yml')
    env.write_text('\n'.join(k+'='+v for k,v in settings.items())+'\n');env.chmod(0o600)
    # Mantener solo servicios usados; todos provienen de un tag fijo.
    compose=yaml.safe_load((SOURCE/'docker-compose.yml').read_text())
    keep=['studio','api-gw','auth','rest','meta','db']
    compose['services']={k:compose['services'][k] for k in keep}
    compose['name']='nexoandes-supabase'
    compose['services']['auth']['environment']['GOTRUE_JWT_KEYS']='${JWT_KEYS}'
    compose['services']['db']['volumes']=[v if not v.startswith('db-config:') else './volumes/db-config:/etc/postgresql-custom' for v in compose['services']['db']['volumes']]
    compose.pop('volumes',None)
    (STACK/'docker-compose.yml').write_text(yaml.safe_dump(compose,sort_keys=False,width=140))
    # Sonda ALB sin clave: solo estado de Auth, sin acceso a usuarios ni datos.
    lds=STACK/'volumes/api/envoy/lds.template.yaml'
    routes_doc=yaml.safe_load(lds.read_text())
    filters=routes_doc['resources'][0]['filter_chains'][0]['filters']
    routes=filters[0]['typed_config']['route_config']['virtual_hosts'][0]['routes']
    health=copy.deepcopy(next(route for route in routes if route.get('name')=='auth-v1-protected'))
    health.update(name='nexoandes-auth-health',match={'path':'/auth/v1/health'})
    health['route'].update(prefix_rewrite='/health',timeout='5s')
    health['typed_per_filter_config']['envoy.filters.http.rbac']={
        '@type':'type.googleapis.com/envoy.extensions.filters.http.rbac.v3.RBACPerRoute',
        'rbac':{'rules':{'action':'ALLOW','policies':{'health':{'permissions':[{'any':True}],'principals':[{'any':True}]}}}}}
    routes.insert(0,health)
    lds.write_text(yaml.safe_dump(routes_doc,sort_keys=False,width=140))
    # old contiene secretos previos; no se distribuye ni se usa como configuración.
    for old in STACK.rglob('*.old'):old.unlink()
    subprocess.run(['docker','compose','--env-file',str(env),'-f',str(STACK/'docker-compose.yml'),'config','--quiet'],check=True,capture_output=True)
    return settings


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--url',required=True);a=p.parse_args()
    prepare(a.url)
    print('Pila validada; secretos privados generados, sin arrancar contenedores.')
