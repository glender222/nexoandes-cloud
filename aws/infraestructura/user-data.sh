#!/bin/bash
set -euo pipefail

# Número final del equipo pendiente de confirmar. Actualizar antes del despliegue.
TEAM_NUMBER="XX"

yum install -y httpd
systemctl enable --now httpd

# IMDSv2 permite mostrar qué instancia respondió sin publicar credenciales.
METADATA_TOKEN=$(curl --silent --show-error --fail --max-time 3 -X PUT \
  -H 'X-aws-ec2-metadata-token-ttl-seconds: 300' \
  http://169.254.169.254/latest/api/token || true)
metadata_value() {
  local path="$1"
  local value
  if [[ -z "$METADATA_TOKEN" ]]; then
    printf 'no disponible'
    return
  fi
  value=$(curl --silent --show-error --fail --max-time 3 \
    -H "X-aws-ec2-metadata-token: $METADATA_TOKEN" \
    "http://169.254.169.254/latest/meta-data/$path" || true)
  printf '%s' "${value:-no disponible}"
}

INSTANCE_ID=$(metadata_value instance-id)
AZ=$(metadata_value placement/availability-zone)

cat > /var/www/html/index.html <<HTML
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>NexoAndes | Catálogo informativo</title>
  <style>
    :root { color-scheme: light; font-family: Arial, Helvetica, sans-serif; }
    body { margin: 0; color: #17324d; background: #f4f7fa; line-height: 1.5; }
    header { background: #123a5c; color: #fff; padding: 2rem max(1.5rem, calc((100% - 70rem)/2)); }
    main { max-width: 70rem; margin: 2rem auto; padding: 0 1.5rem; }
    h1 { margin: .3rem 0; font-size: clamp(2rem, 4vw, 3rem); }
    .tag { color: #bce3ff; font-weight: bold; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr)); gap: 1rem; }
    .card { background: #fff; border: 1px solid #d9e3eb; border-radius: .7rem; padding: 1.25rem; box-shadow: 0 2px 8px #10324f0d; }
    .proof { margin-top: 2rem; background: #e3eff7; border-left: .35rem solid #1779ab; padding: 1rem 1.25rem; }
    footer { max-width: 70rem; margin: 2rem auto; padding: 0 1.5rem 2rem; color: #526778; }
  </style>
</head>
<body>
  <header>
    <div class="tag">Proyecto Cloud – Equipo $TEAM_NUMBER</div>
    <h1>NexoAndes Distribución</h1>
    <p>Catálogo informativo de suministros para negocios de Lima y Arequipa.</p>
  </header>
  <main>
    <h2>Conoce nuestras líneas</h2>
    <div class="grid">
      <section class="card"><h3>Papel y archivo</h3><p>Materiales para el trabajo diario de oficinas y comercios.</p></section>
      <section class="card"><h3>Impresión</h3><p>Suministros para equipos de impresión y etiquetado.</p></section>
      <section class="card"><h3>Organización</h3><p>Accesorios para ordenar documentos y espacios de trabajo.</p></section>
    </div>
    <section class="proof">
      <h2>Arquitectura V1</h2>
      <p>Portal académico publicado mediante un balanceador y servidores web en AWS Academy.</p>
      <p><strong>Instancia que respondió:</strong> $INSTANCE_ID · <strong>Zona:</strong> $AZ</p>
    </section>
  </main>
  <footer>Portal informativo de demostración. Los pedidos y el inventario en línea corresponden a fases posteriores.</footer>
</body>
</html>
HTML
