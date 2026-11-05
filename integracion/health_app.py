#!/usr/bin/env python3
"""Sonda HTTP de continuidad: consulta PostgreSQL sin exponer datos de negocio."""
import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            content = ('<!doctype html><html lang="es"><meta charset="utf-8">'
                       '<title>NexoAndes</title><h1>NexoAndes</h1>'
                       '<p>Portal de contingencia del proyecto Cloud.</p>'
                       '<p>Proyecto Cloud – Equipo '+os.environ.get('TEAM_NUMBER','XX')+'</p>'
                       '<p><a href="/health">Comprobar continuidad de PostgreSQL</a></p></html>').encode()
            self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8')
        elif self.path == '/health':
            env = dict(os.environ, PGCONNECT_TIMEOUT='3')
            query = "SELECT json_build_object('recovery',pg_is_in_recovery(),'probe',COALESCE((SELECT max(id) FROM public.nexoandes_continuity_probe),0))::text"
            try:
                p = subprocess.run(['/usr/bin/psql','-X','-At','-v','ON_ERROR_STOP=1','-c',query],env=env,capture_output=True,text=True,timeout=5)
                if p.returncode: raise ValueError('database unavailable')
                data = {'ok':True,'site':os.environ.get('NEXO_SITE','unknown'),'database':json.loads(p.stdout)}
                self.send_response(200)
            except (ValueError,subprocess.TimeoutExpired):
                data = {'ok':False,'site':os.environ.get('NEXO_SITE','unknown'),'database':'unavailable'}
                self.send_response(503)
            content=json.dumps(data).encode();self.send_header('Content-Type','application/json')
        else:
            self.send_response(404);content=b'Not found'
        self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(content)))
        self.end_headers();self.wfile.write(content)

    def log_message(self,*args):
        pass


if __name__=='__main__':
    ThreadingHTTPServer((os.environ.get('NEXO_BIND','127.0.0.1'),int(os.environ.get('NEXO_PORT','8081'))),Handler).serve_forever()
