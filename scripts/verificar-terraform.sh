#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
./nexoandes validar
python3 -m unittest discover -s infraestructura/tests -v
for CLOUD in aws azure gcp; do
  TF_DATA_DIR="$ROOT/infraestructura/privado/validacion/$CLOUD" \
    "$ROOT/infraestructura/privado/bin/terraform" -chdir="$CLOUD/terraform" test -no-color
done
