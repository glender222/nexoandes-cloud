"""Autorización HTTP del backend: una pantalla de login no otorga acceso por sí sola."""
import importlib.util
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import threading
import unittest
from unittest.mock import patch
from urllib.request import Request,urlopen
from urllib.error import HTTPError

spec=importlib.util.spec_from_file_location('portal_auth',Path(__file__).parents[2]/'integracion/supabase/portal_backend.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class Auth(BaseHTTPRequestHandler):
    calls=0
    def do_GET(self):
        Auth.calls+=1
        status=200 if self.headers.get('Authorization')=='Bearer validado-por-auth' else 401
        data={'id':'usuario-prueba','email':'prueba@example.invalid'} if status==200 else {'error':'invalid'}
        self.send_response(status);self.end_headers();self.wfile.write(json.dumps(data).encode())
    def log_message(self,*args):pass


class AutorizacionSupabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.auth=ThreadingHTTPServer(('127.0.0.1',0),Auth)
        cls.backend=ThreadingHTTPServer(('127.0.0.1',0),module.Handler)
        cls.env=patch.dict(module.os.environ,{'SUPABASE_INTERNAL_URL':f'http://127.0.0.1:{cls.auth.server_port}','SUPABASE_PUBLISHABLE_KEY':'publicable-de-prueba'})
        cls.env.start()
        for server in [cls.auth,cls.backend]:threading.Thread(target=server.serve_forever,daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        for server in [cls.auth,cls.backend]:server.shutdown();server.server_close()
        cls.env.stop()

    def request(self,token=None):
        headers={'Authorization':'Bearer '+token} if token else {}
        request=Request(f'http://127.0.0.1:{self.backend.server_port}/api/privado',headers=headers)
        try:
            with urlopen(request,timeout=3) as r:return r.status,json.load(r)
        except HTTPError as r:return r.code,json.load(r)

    def test_sin_token_no_llama_auth_y_rechaza(self):
        before=Auth.calls
        self.assertEqual(self.request()[0],401)
        self.assertEqual(Auth.calls,before)

    def test_token_inventado_no_otorga_acceso(self):
        self.assertEqual(self.request('inventado')[0],401)

    def test_identidad_viene_del_servicio_auth(self):
        status,data=self.request('validado-por-auth')
        self.assertEqual(status,200)
        self.assertEqual(data['usuario'],'usuario-prueba')


if __name__=='__main__':unittest.main()
