# Avances de OCI

**Última revisión local:** 2026-10-22. Terraform validado y OCI CLI instalada; no se consultó una cuenta OCI.

| Elemento | Estado | Siguiente paso |
|---|---|---|
| Cuenta y tenancy | No configuradas en el historial | Confirmar cuenta, permisos y compartment |
| OCI CLI y clave API | CLI 3.95.1 instalada; perfil API ausente ([INC-008](../incidencias/REGISTRO.md)) | Preparar acceso local y verificar identidad |
| Red y recursos | Terraform preparado, sin despliegue real | Verificar cuenta y capacidad antes de planificar |
| Integración multicloud | No probada | Definir flujo y prueba con AWS y Azure |

Cuando se ejecute trabajo nuevo, añade fecha, recurso, comando o procedimiento, resultado y enlace a evidencia. Registra incidencias nuevas solo en `../incidencias/REGISTRO.md`.

## Preparación Terraform — 22/10/2026

- Se creó `oci/terraform/` con VCN, Object Storage versionado/rotación, VM A1 limitada a 2 OCPU/12 GB y 50 GB de arranque y Bastion opcional. El apagado detiene la misma VM y conserva datos. Terraform 1.17.0 / OCI 9.11.0 fijados con lockfile.
- `terraform validate` correcto y dos pruebas `terraform test` con proveedor simulado: RUNNING → STOPPED conservando VM y bucket. No hubo consultas autenticadas ni despliegue real de OCI.
- Revisión local: `oci` no está en PATH y `oci/privado/` no tiene un perfil API configurado (INC-008). Faltan tenancy, región home, compartment, dominio de disponibilidad e imagen Ubuntu ARM64.
- OCI queda deshabilitada en la configuración privada del control hasta completar acceso y verificar capacidad/consumo Always Free. La instalación de strongSwan no configura automáticamente un túnel, y no hay replicación PostgreSQL demostrada. Guía: [Control multicloud](../infraestructura/README.md).

## Preparación de acceso local — 22/10/2026

- `./scripts/instalar-oci-cli.sh` instaló OCI CLI 3.95.1 mediante PyPI en `infraestructura/privado/oci-cli`, con enlace local `infraestructura/privado/bin/oci`. `--version` correcto; no se modificaron Python del sistema ni archivos de inicio del shell.
- Se añadió un ejemplo sin secretos y el procedimiento en `ACCESO.md`. No existe aún `oci/privado/config` ni se ha autenticado una cuenta: el acceso API sigue siendo el requisito pendiente de INC-008. La instalación de la CLI no acredita acceso a OCI.
