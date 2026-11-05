#!/usr/bin/env python3
"""Instalación local del login en una web nueva; no utiliza secretos administrativos."""
from pathlib import Path
import json
import subprocess
import sys

base=Path(__file__).resolve().parent
host,key=sys.argv[1:]
if not key.startswith('sb_publishable_'):raise SystemExit('Se requiere clave publicable')
web=Path('/var/www/html/acceso');web.mkdir(parents=True,exist_ok=True)
for source,target in [('acceso.html','index.html'),('acceso.js','acceso.js'),('estilo.css','estilo.css')]:
    (web/target).write_text((base/source).read_text());(web/target).chmod(0o644)
(web/'config.js').write_text('const NEXO_SUPABASE = {url: window.location.origin, publicKey: '+json.dumps(key)+'};\n')
(web/'config.js').chmod(0o644)
app=Path('/opt/nexoandes');app.mkdir(parents=True,exist_ok=True)
(app/'portal_backend.py').write_text((base/'portal_backend.py').read_text());(app/'portal_backend.py').chmod(0o644)
env=Path('/etc/nexoandes/supabase.env');env.parent.mkdir(parents=True,exist_ok=True)
env.write_text(f'SUPABASE_INTERNAL_URL=http://{host}:8000\nSUPABASE_PUBLISHABLE_KEY={key}\n');env.chmod(0o600)
Path('/etc/systemd/system/nexoandes-portal-auth.service').write_text('''[Unit]
Description=Validacion Supabase NexoAndes
After=network-online.target
[Service]
User=nobody
EnvironmentFile=/etc/nexoandes/supabase.env
ExecStart=/usr/bin/python3 /opt/nexoandes/portal_backend.py
Restart=always
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
[Install]
WantedBy=multi-user.target
''')
Path('/etc/httpd/conf.d/nexoandes-supabase.conf').write_text('''ProxyPass "/api/privado" "http://127.0.0.1:8082/api/privado"
ProxyPassReverse "/api/privado" "http://127.0.0.1:8082/api/privado"
<Directory "/var/www/html/acceso">
 Header always set Cache-Control "no-store"
 Header always set X-Content-Type-Options "nosniff"
 Header always set Referrer-Policy "no-referrer"
</Directory>
''')
index=Path('/var/www/html/index.html');text=index.read_text()
if '/acceso/index.html' not in text:index.write_text(text.replace('</body>','<p style="text-align:center"><a href="/acceso/index.html">Acceso al portal</a></p></body>'))
subprocess.run(['systemctl','daemon-reload'],check=True)
subprocess.run(['systemctl','enable','--now','nexoandes-portal-auth'],check=True)
subprocess.run(['systemctl','restart','nexoandes-portal-auth'],check=True)
