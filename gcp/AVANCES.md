# Registro de Avances — Google Cloud Platform (GCP)

## 28/10/2026 — Decisión Arquitectónica y Conexión Exitosa

* **Sustitución de Proveedor:** OCI fue sustituido por Google Cloud (GCP) como el tercer proveedor de la arquitectura multicloud.
* **Proyecto Activo:**
  - ID del Proyecto: `gen-lang-client-0623826791`
  - Número de Proyecto: `816654945610`
  - Región base: `us-central1`
* **Autenticación:**
  - Cuenta de servicio: `gen-lang-client-0623826791@gen-lang-client-0623826791.iam.gserviceaccount.com`
  - Clave privada guardada de forma segura en `gcp/privado/sa-key.json` (permisos 600, excluida de Git).
* **Validación Técnica:**
  - Proveedor Terraform `hashicorp/google v5.45.2` inicializado exitosamente en `gcp/terraform/`.
  - `./nexoandes comprobar --nube gcp` ejecutado con éxito: validación de identidad y permisos positiva.
  - `./nexoandes plan encender --nube gcp` ejecutado con éxito: plan preparado para VPC (`10.30.0.0/16`), subred (`10.30.1.0/24`) y Cloud Storage Bucket (`nexoandes-backup-gen-lang-client-0623826791`).
* **Estado:** Conexión activa y comprobada. Recursos aún no aplicados (listos para encender cuando el usuario lo autorice).

## 29/10/2026 — Despliegue, Validación Multicloud y Apagado Seguro de Contingencia

* **Despliegue de Infraestructura GCP (Terraform):**
  - Se aprovisionó la VPC `nexoandes-gcp-vpc` (`10.30.0.0/16`) y la subred `nexoandes-gcp-subnet` (`10.30.1.0/24`).
  - Bucket de almacenamiento de respaldo `nexoandes-backup-gen-lang-client-0623826791` con versionado activado.
  - Reglas de firewall `nexoandes-gcp-allow-ssh` (puerto 22 e ICMP).
  - VM en contingencia DRP `nexoandes-gcp-standby` (`e2-micro`, Debian 12, disco 10GB, IP pública `34.29.38.228`).
* **Prueba de Integridad Multicloud (P5):**
  - Sincronización del volcado PostgreSQL `20261029T162807Z.dump` (1,868 bytes) en Cloud Storage.
  - Verificación de hash SHA-256 (`39941843837fc2570e8becafaf244ef3e019a150b956c62c79537edc886423bb`) coincidente al 100% con AWS S3 y Azure Blob Storage.
* **Apagado y Destrucción de Cómputo (`./nexoandes apagar --nube gcp`):**
  - Se ejecutó el apagado controlado mediante Terraform, destruyendo la máquina virtual `google_compute_instance.vm` en 23 segundos.
  - Auditoría directa a la API REST de GCP Compute Engine confirmando 0 instancias en ejecución (`GCP Instances: []`).
  - Preservación del bucket y red VPC sin costos recurrentes ($0.00 / hora).


## Comprobación de acceso — 04/11/2026

- Consulta realizada el 04/11/2026 10:33 (America/Lima) mediante la cuenta de servicio existente en el archivo privado configurado, con autorización del usuario para comprobar el acceso actual; no se creó proyecto ni se reemplazó la clave.
- Proyecto configurado y proyecto de la clave coinciden: `gen-lang-client-0623826791`, región de trabajo `us-central1`. Autenticación OAuth correcta.
- Compute `instances.aggregatedList` respondió HTTP 200; lectura de metadatos del bucket `nexoandes-backup-gen-lang-client-0623826791` respondió HTTP 200, ubicación `US-CENTRAL1`. No se concluye inventario completo a partir de esta consulta acotada.
- La primera consulta Compute usó un scope que esa API no admite; se corrigió a `compute.readonly` y `devstorage.read_only` y se repitió correctamente. No se cambiaron roles IAM.
- La clave existente funciona para estas lecturas y no requiere reemplazo por este resultado. No se comprobaron permisos de escritura, saldo ni créditos. Tokens únicamente en memoria, sin incluirlos en evidencias.
- Sin cambios en recursos ni credenciales. [Resultado de las consultas](../infraestructura/evidencias/acceso-20261104.json).

## Continuidad V2 y pruebas — 04/11/2026

- Proyecto `gen-lang-client-0623826791`, `us-central1-a`, cuenta de servicio existente con consulta real Compute autorizada; OCI permanece histórico.
- Se implementó una VM e2-micro persistente, arranque 10 GB y disco de datos separado de 20 GB, ambos pd-standard, bucket privado/versionado y reglas específicas. El presupuesto declarado es US$10/mes; saldo/vencimiento no verificados por API (INC-017).
- VM numérica `2724455023399856729`; disco de datos `4142628206354557535`. `apagar` detiene la misma VM y conserva datos; se migró startup-script a metadata editable sin recrear la VM.
- IPsec strongSwan y réplica PostgreSQL física con slot y WAL acotado; puerto 5432 sin regla pública. PSK y contraseñas en material privado, fuera de Terraform/evidencias.
- Se promovió GCP tras aislar el primario, se escribió un marcador, se probó portal alternativo con los procesos AWS detenidos y se devolvió el primario a AWS sin perder cinco filas sintéticas. Restauraciones desde Azure y GCP verificadas con SQL.
- Administración SSH restringida desde gateway AWS por SSM; SSH local tuvo timeout (INC-020). El reencendido detectó IP efímera vacía (INC-023), se corrigió la reconciliación. La nueva IP HTTP fue bloqueada por FortiGuard local; servicio consultado desde AWS (INC-024).
- La réplica apagada no recibe WAL. No hay conmutación DNS automática, capacidad de producción demostrada ni garantía de costo cero. No se modificó la política de red local.

Comandos: `./nexoandes continuidad`, scripts de pruebas en `integracion/`, `./nexoandes apagar` e `inventario.py`. Evidencias: [estado y límites](../diagramas/excalidraw/ESTADO_2026-11-04.md), [ensayos reales](../integracion/evidencias/20261104/), [inventario final](../infraestructura/evidencias/inventario-final-20261104.json). Las capturas de consola y datos del equipo siguen pendientes; no se modificó el texto de los informes.

Cierre 04/11/2026 14:18 (America/Lima): API confirmó el apagado NexoAndes y la conservación de datos/respaldos. [Comprobación](../integracion/evidencias/20261104/cierre.json). Ciclo final: siete filas coincidentes y restauración de ambas copias con siete filas; [persistencia](../integracion/evidencias/20261104/persistencia-ciclo.json), [restauraciones](../integracion/evidencias/20261104/restauracion-ciclo.json).

## Pausa solicitada — 04/11/2026 14:36 (America/Lima)

Se ejecutó `./nexoandes apagar` y se verificó por API el estado de las tres nubes. NexoAndes no tiene cómputo activo; datos, redes y respaldos conservados. Timer local `nexoandes-respaldos.timer` detenido y deshabilitado por esta pausa; su servicio está inactivo. Las VMs de examen AWS y Antigravity Azure, ajenas al proyecto, permanecen sin cambios. [Evidencia](../integracion/evidencias/20261104/pausa-solicitada.json), [inventario](../infraestructura/evidencias/inventario-pausa-20261104.json). Para reactivar las copias periódicas, consultar `integracion/CONTINUIDAD.md`.

## Supabase autohospedado — 04/11/2026 21:55 (America/Lima)

Se recibió por HTTPS una copia del respaldo Supabase generado en AWS; descarga y SHA256 coincidentes entre los tres proveedores. No se arrancó ni creó cómputo de NexoAndes en esta nube. La restauración selectiva de usuarios se probó en una BD temporal AWS, no se afirma restauración integral o failover Supabase en gcp.

Comandos: `integracion/desplegar_supabase.py --ejecutar`, `integracion/supabase/verificar.py`, `integracion/respaldos.py --tipo supabase --generar`; guía reproducible `./nexoandes supabase`. [Estado y evidencia](../integracion/evidencias/20261104/supabase/ESTADO.json), [operación](../integracion/SUPABASE.md), [inventario actual](../infraestructura/evidencias/inventario-supabase-20261104.json). No se modificaron los textos INFORME ni se completaron las capturas de consola pendientes del usuario.


## Revisión del mapa y estado — 04/11/2026 23:01 (America/Lima)

Se confirmó acceso con `./nexoandes comprobar` y se consultaron identidades/recursos de las tres nubes, sin encender, apagar ni cambiar infraestructura. [Inventario de lectura](../infraestructura/evidencias/inventario-mapa-20261104.json): cinco EC2 NexoAndes en ejecución (dos web, PostgreSQL, Supabase y gateway); VM GCP TERMINATED; bucket GCP, Storage y VNet Azure presentes. La VM Azure ajena al proyecto permanece fuera del mapa. No se repitieron pruebas de aplicaciones ni se consultó Cloud Billing API, cuyo bloqueo ya estaba registrado.

El [mapa detallado](../diagramas/excalidraw/nexoandes-multicloud-detallado.excalidraw) incorpora el rol SaaS académico de Supabase, iconos oficiales AWS, detalle de servicios GCP dentro de una sola VM y recursos Azure desglosados. Se retiró la laptop de la topología de servicio; las copias representan flujo lógico bajo demanda, conservando su mecanismo operativo real en la documentación. Exportaciones PNG/SVG regeneradas y revisadas.

## IAM básico — 05/11/2026 (America/Lima)

Se comprobó proyecto gen-lang-client-0623826791/us-central1 y cuenta de servicio existente. GET IAM del bucket y testPermissions correctos (get/list/create/delete de objetos); cargas/descargas y SHA256 contrastados con S3/Azure. projects:getIamPolicy bloqueado por Cloud Resource Manager API deshabilitada (INC-031); no se habilitó ni se modificaron roles globales. La VM sigue TERMINATED y no tiene SA adjunta; no se arrancó cómputo.

Comandos: `./nexoandes comprobar`, `python3 integracion/auditar_iam.py`, consultas CLI/API y `python3 integracion/respaldos.py --tipo postgresql` / `--tipo supabase`. [Alcance, identidades y evidencia](../integracion/IAM.md). Credenciales y planes completos se mantienen privados; no se modificó cómputo ni la configuración del portal.
