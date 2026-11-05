#!/bin/bash
set -euo pipefail
umask 077
source /etc/nexoandes/supabase-backup.env
cd /srv/supabase
exec 9>/run/nexoandes-supabase-backup.lock
flock -n 9 || exit 0
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
BASE=/var/lib/nexoandes-supabase-backups
install -d -m 700 "$BASE"
WORK=$(mktemp -d "$BASE/.trabajo-XXXXXX")
trap 'rm -rf "$WORK"' EXIT
docker compose exec -T db pg_dump -U postgres -Fc postgres > "$WORK/database.dump"
docker compose exec -T db pg_dumpall -U postgres --globals-only > "$WORK/roles.sql"
if [[ "$(docker compose exec -T db psql -U postgres -Atc "SELECT 1 FROM pg_database WHERE datname='_supabase'")" == 1 ]]; then
  docker compose exec -T db pg_dump -U postgres -Fc _supabase > "$WORK/internal.dump"
fi
tar --exclude='./volumes/db/data' --exclude='./.fallos' --exclude='./.env.old' -czf "$WORK/configuracion.tgz" -C /srv/supabase .
ARCHIVE="$BASE/$STAMP.tgz"
tar -czf "$ARCHIVE" -C "$WORK" .
chmod 600 "$ARCHIVE"
sha256sum "$ARCHIVE" > "$ARCHIVE.sha256"
# Bucket privado con SSE; no imprimir dumps, roles ni configuracion.
aws s3api put-object --region us-east-1 --bucket "$NEXO_BACKUP_BUCKET" --key "supabase/$STAMP.tgz" --body "$ARCHIVE" --server-side-encryption AES256 >/dev/null
find "$BASE" -maxdepth 1 -type f -name '*.tgz*' -mtime +2 -delete
echo "RESPALDO_SUPABASE_CREADO $STAMP"
