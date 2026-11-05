#!/usr/bin/env python3
"""Backend mínimo: comprueba el token contra Auth; no confía en claims del navegador."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import os
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path!='/api/privado':
            self.send_response(404);self.end_headers();return
        token=self.headers.get('Authorization','')
        status=401;data={'ok':False,'error':'Se requiere una sesión válida'}
        if token.startswith('Bearer ') and len(token)<16000:
            request=Request(os.environ['SUPABASE_INTERNAL_URL']+'/auth/v1/user',
                            headers={'Authorization':token,'apikey':os.environ['SUPABASE_PUBLISHABLE_KEY']})
            try:
                with urlopen(request,timeout=5) as response:user=json.load(response)
                if user.get('id'):
                    status=200;data={'ok':True,'usuario':user['id'],'email':user.get('email'),'mensaje':'Sesión validada en el backend de NexoAndes'}
            except HTTPError as error:
                if error.code>=500:status=503;data={'ok':False,'error':'Autenticación temporalmente no disponible'}
            except (URLError,TimeoutError,ValueError):
                status=503;data={'ok':False,'error':'Autenticación temporalmente no disponible'}
        content=json.dumps(data,ensure_ascii=False).encode()
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(content)))
        self.end_headers();self.wfile.write(content)

    def log_message(self,*args):pass


if __name__=='__main__':ThreadingHTTPServer(('127.0.0.1',8082),Handler).serve_forever()
