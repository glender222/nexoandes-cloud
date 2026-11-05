# Oracle Cloud Infrastructure (OCI) [Histórico / Reemplazado]

> **Nota (28/10/2026):** OCI ha sido reemplazado por **Google Cloud (GCP)** como el tercer proveedor de la arquitectura multicloud por decisión del usuario. Este directorio y sus archivos se conservan como referencia histórica. Consulta [gcp/README.md](../gcp/README.md) para el nuevo proveedor planificado.

OCI tiene Terraform validado y OCI CLI 3.95.1 instalada localmente el 22/10/2026. Falta configurar el acceso API; no se han consultado ni desplegado recursos de una cuenta Oracle. Permanece deshabilitada en el control común hasta verificar tenancy, región home, permisos y capacidad.

- [ACCESO.md](ACCESO.md): preparación del perfil y comprobación de acceso.
- [AVANCES.md](AVANCES.md): estado y próximos pasos.
- [Terraform](terraform/README.md): VCN, Object Storage y VM A1 con control de encendido, administrados desde el [control común](../infraestructura/README.md). La nube permanece deshabilitada hasta configurar la cuenta y el perfil API.
- `infraestructura/`: ubicación futura del código y configuraciones desplegables.
- `privado/`: clave API y configuración local si se crean; no va en entregables.

OCI está prevista para réplica PostgreSQL y copia de respaldos, según [integracion/README.md](../integracion/README.md); esas funciones aún no están configuradas ni probadas.
