#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
python3 "$ROOT/infraestructura/control.py" configurar
python3 -c 'import gi; gi.require_version("Gtk", "3.0"); from gi.repository import Gtk'
python3 - "$ROOT" <<'PY'
from pathlib import Path
import sys
root=Path(sys.argv[1])
target=Path.home()/'.local/share/applications/nexoandes-lab.desktop'
target.parent.mkdir(parents=True,exist_ok=True)
# Desktop Entry requiere comillas dobles y escape independiente de una shell.
exe=str(root/'nexoandes').replace('\\','\\\\').replace('"','\\"').replace('`','\\`').replace('$','\\$').replace('%','%%')
target.write_text('[Desktop Entry]\nType=Application\nName=NexoAndes — Control multicloud\nComment=Encender y apagar el laboratorio con Terraform\nExec="'+exe+'" panel\nIcon=network-server\nTerminal=false\nCategories=Development;\n')
target.chmod(0o644)
print('Lanzador creado:',target)
PY
