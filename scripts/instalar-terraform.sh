#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
VERSION=1.17.0
case "$(uname -m)" in
  x86_64) ARCH=amd64 ;;
  aarch64) ARCH=arm64 ;;
  *) printf 'Arquitectura no soportada por este instalador.\n' >&2; exit 1 ;;
esac
DEST="$ROOT/infraestructura/privado/bin"
mkdir -p "$DEST"
chmod 700 "$ROOT/infraestructura/privado" "$DEST"
if [[ -x "$DEST/terraform" ]] && "$DEST/terraform" version -json | python3 -c 'import json,sys;sys.exit(json.load(sys.stdin)["terraform_version"] != "1.17.0")'; then
  printf 'Terraform %s ya está instalado en %s\n' "$VERSION" "$DEST/terraform"
  exit 0
fi
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
ZIP="terraform_${VERSION}_linux_${ARCH}.zip"
BASE="https://releases.hashicorp.com/terraform/$VERSION"
curl --fail --silent --show-error --location "$BASE/$ZIP" -o "$WORK/$ZIP"
curl --fail --silent --show-error --location "$BASE/terraform_${VERSION}_SHA256SUMS" -o "$WORK/SHA256SUMS"
python3 - "$WORK" "$ZIP" "$DEST" <<'PY'
import hashlib,pathlib,sys,zipfile
work,name,dest=pathlib.Path(sys.argv[1]),sys.argv[2],pathlib.Path(sys.argv[3])
checks={line.split()[1].lstrip('*'):line.split()[0] for line in (work/'SHA256SUMS').read_text().splitlines()}
assert hashlib.sha256((work/name).read_bytes()).hexdigest()==checks[name], 'Checksum incorrecto'
with zipfile.ZipFile(work/name) as archive:
    (dest/'terraform').write_bytes(archive.read('terraform'))
(dest/'terraform').chmod(0o700)
print('Descarga oficial y SHA256 comprobados:',dest/'terraform')
PY
"$DEST/terraform" version
