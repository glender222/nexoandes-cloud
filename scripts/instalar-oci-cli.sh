#!/usr/bin/env bash
set -euo pipefail
umask 077
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
VERSION=3.95.1
DEST="$ROOT/infraestructura/privado"
mkdir -p "$DEST/bin"
chmod 700 "$DEST" "$DEST/bin"
python3 -m venv "$DEST/oci-cli"
"$DEST/oci-cli/bin/python" -m pip install --disable-pip-version-check "oci-cli==$VERSION"
ln -sfn ../oci-cli/bin/oci "$DEST/bin/oci"
"$DEST/bin/oci" --version
