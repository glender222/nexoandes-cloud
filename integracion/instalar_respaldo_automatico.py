#!/usr/bin/env python3
"""Instalar un temporizador de usuario; no enciende recursos cloud."""
import json
from pathlib import Path
import subprocess
from datetime import datetime,timezone
import operaciones as op

root=op.ROOT
directory=Path.home()/'.config/systemd/user'
directory.mkdir(parents=True,exist_ok=True)
service=f'''[Unit]
Description=Copiar y comprobar el ultimo respaldo NexoAndes
After=network-online.target
[Service]
Type=oneshot
WorkingDirectory={root}
Environment=PATH={Path.home()}/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/bin/python3 {root}/integracion/respaldos.py
TimeoutStartSec=300
NoNewPrivileges=true
'''
timer='''[Unit]
Description=Copias NexoAndes cada hora mientras el equipo esta disponible
[Timer]
OnCalendar=hourly
RandomizedDelaySec=5min
Persistent=true
[Install]
WantedBy=timers.target
'''
for name,body in [('nexoandes-respaldos.service',service),('nexoandes-respaldos.timer',timer)]:
    path=directory/name;path.write_text(body);path.chmod(0o644)
for args in [['daemon-reload'],['enable','--now','nexoandes-respaldos.timer']]:
    subprocess.run(['systemctl','--user',*args],check=True,capture_output=True,text=True)
result={'utc':datetime.now(timezone.utc).isoformat(),'timer':'nexoandes-respaldos.timer','ejecutor':'equipo local','periodicidad':'cada hora, retraso aleatorio hasta 5 minutos','requiere':'sesion de usuario/equipo disponible, red y credenciales vigentes','no_enciende_recursos':True}
for field,args in [('habilitado',['is-enabled','nexoandes-respaldos.timer']),('estado',['is-active','nexoandes-respaldos.timer']),('siguiente',['show','nexoandes-respaldos.timer','--property=NextElapseUSecRealtime','--value'])]:
    result[field]=subprocess.run(['systemctl','--user',*args],capture_output=True,text=True,check=True).stdout.strip()
(root/'integracion/evidencias/20261104/temporizador.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
