#!/usr/bin/env python3
"""Verifica Studio externo sin registrar credenciales ni cuerpos administrativos."""
import base64
from datetime import datetime, timezone
import json
from pathlib import Path
import ssl
import sys
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPSHandler, HTTPRedirectHandler

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'integracion'))
import operaciones as op


def main():
    op.assert_aws_identity()
    state = op.state('aws')
    url = state.get('supabase_studio_url')
    if not url or urlsplit(url).scheme != 'https':
        raise RuntimeError('Studio externo no está habilitado con HTTPS')
    target = urlsplit(url)
    context = ssl.create_default_context(cafile=str(op.PRIVATE/'tls/alb.crt'))

    class SameOrigin(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            p = urlsplit(newurl)
            if (p.scheme, p.hostname, p.port) != (target.scheme, target.hostname, target.port):
                raise RuntimeError('Studio devolvió una redirección fuera de su origen HTTPS')
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    opener = build_opener(HTTPSHandler(context=context), SameOrigin())
    path = op.PRIVATE/'supabase/acceso-administracion.json'
    admin = json.loads(path.read_text())
    valid = base64.b64encode((admin['usuario']+':'+admin['password']).encode()).decode()
    invalid = base64.b64encode((admin['usuario']+':incorrecta-para-prueba').encode()).decode()

    def get(route, credential=None):
        headers = {'Authorization':'Basic '+credential} if credential else {}
        try:
            with opener.open(Request(url+route, headers=headers), timeout=25) as r:
                data = r.read()
                return r.status, '<html' in data.decode(errors='ignore').lower()
        except HTTPError as r:
            return r.code, False

    checks = {}
    for name, route, credential, expected in [
        ('sin_credenciales','/',None,401),
        ('incorrectas','/',invalid,401),
        ('api_studio_sin_credenciales','/api/platform/projects',None,401),
        ('meta_externo_bloqueado','/pg/tables',None,403),
        ('mcp_bloqueado','/mcp',None,403),
        ('api_mcp_bloqueado','/api/mcp',None,403),
        ('panel_autenticado','/',valid,200),
    ]:
        code, html = get(route, credential)
        checks[name] = code
        if code != expected or (name == 'panel_autenticado' and not html):
            raise RuntimeError(f'Prueba {name}: HTTP {code}; esperado {expected}')
    admin['url_externa'] = url
    op.control.save_json(path, admin)
    result = {'utc':datetime.now(timezone.utc).isoformat(), 'url':url,
              'checks':checks,'tls':'Firma y nombre verificados con CA académica, sin -k',
              'credenciales':'Archivo privado modo 600; no incluidas en evidencia',
              'completo':True}
    dest = ROOT/'integracion/evidencias/20261104/supabase/studio-externo.json'
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
