#!/usr/bin/env python3
"""Pruebas reales de Auth y autorización, sin escribir tokens ni contraseñas en evidencias."""
from datetime import datetime,timezone
from pathlib import Path
import importlib.util
import json
import ssl
import sys
from urllib.request import Request,urlopen
from urllib.error import HTTPError

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'integracion'))
import operaciones as op
from desplegar_supabase import preparer


def main():
    op.assert_aws_identity();aws=op.state('aws');base=aws['https_url']
    settings=preparer.read_env(preparer.STACK/'.env')
    demo=json.loads((preparer.PRIVATE/'acceso-demo.json').read_text())
    context=ssl.create_default_context(cafile=str(op.PRIVATE/'tls/alb.crt'))
    def request(path,body=None,token=None,admin=False,http=False):
        headers={'apikey':settings['SUPABASE_SECRET_KEY'] if admin else settings['SUPABASE_PUBLISHABLE_KEY']}
        if token:headers['Authorization']='Bearer '+token
        if admin:headers['Authorization']='Bearer '+settings['SERVICE_ROLE_KEY_ASYMMETRIC']
        data=None
        if body is not None:headers['Content-Type']='application/json';data=json.dumps(body).encode()
        req=Request((aws['url'] if http else base)+path,headers=headers,data=data)
        try:
            with urlopen(req,timeout=15,context=context) as r:
                content=r.read();return r.status,json.loads(content) if content.startswith(b'{') else None
        except HTTPError as r:
            content=r.read();return r.code,json.loads(content) if content.startswith(b'{') else None
    checks={}
    status,health=request('/auth/v1/health');checks['salud_auth']=status;assert status==200
    status,listing=request('/auth/v1/admin/users?page=1&per_page=50',admin=True);assert status==200
    user=next((u for u in listing['users'] if u['email']==demo['email']),None)
    if user is None:
        status,user=request('/auth/v1/admin/users',body={'email':demo['email'],'password':demo['password'],'email_confirm':True},admin=True)
        assert status in [200,201]
    checks['cuenta_demo_confirmada']=bool(user.get('email_confirmed_at'))
    status,_=request('/auth/v1/token?grant_type=password',body={'email':demo['email'],'password':'incorrecta-para-prueba'})
    checks['clave_incorrecta']=status;assert status in [400,401,422]
    status,_=request('/api/privado');checks['backend_sin_token']=status;assert status==401
    status,_=request('/api/privado',token='token-inventado');checks['backend_token_inventado']=status;assert status==401
    status,session=request('/auth/v1/token?grant_type=password',body=demo)
    checks['login_correcto']=status;assert status==200 and session.get('access_token')
    token=session['access_token']
    status,identity=request('/auth/v1/user',token=token);checks['identidad_auth']=status;assert status==200 and identity['id']==user['id']
    status,protected=request('/api/privado',token=token);checks['backend_con_token']=status
    assert status==200 and protected['usuario']==user['id']
    status,_=request('/auth/v1/health',http=True);checks['auth_sobre_http_bloqueado']=status;assert status==403
    status,_=request('/auth/v1/signup',body={'email':'registro-no-habilitado@example.invalid','password':'clave-inutil-de-prueba'})
    checks['autoregistro_deshabilitado']=status;assert status in [400,401,403,422]
    status,_=request('/auth/v1/logout',body={},token=token);checks['logout']=status;assert status in [200,204]
    status,_=request('/api/privado',token=token);checks['token_previo_tras_logout']=status
    admin_access={'tunel_local':'http://127.0.0.1:8800','usuario':settings['DASHBOARD_USERNAME'],'password':settings['DASHBOARD_PASSWORD']}
    if aws.get('supabase_studio_url'):
        admin_access['url_externa']=aws['supabase_studio_url']
    admin_file=preparer.PRIVATE/'acceso-administracion.json'
    admin_file.write_text(json.dumps(admin_access,indent=2)+'\n');admin_file.chmod(0o600)
    proof={'utc':datetime.now(timezone.utc).isoformat(),'url':base,'login':base+'/acceso/','checks':checks,'token_expira_segundos':session['expires_in'],'alcance':'Prueba de autenticacion y endpoint de identidad propio; no modulo comercial completo','tls':'Nombre y certificado verificados con CA academica local, sin desactivar validacion TLS','correos_sms_enviados':False,'cuenta_demo':'Asignada administrativamente con email .invalid; credenciales solo en privado','tokens_en_evidencia':False,'completo':True}
    out=ROOT/'integracion/evidencias/20261104/supabase/pruebas-auth.json';out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(proof,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
