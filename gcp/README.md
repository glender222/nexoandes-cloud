# Google Cloud — contingencia NexoAndes

**Acceso e implementación verificados el 04/11/2026.** Proyecto `gen-lang-client-0623826791`, región `us-central1`. Usar la cuenta de servicio existente en `privado/`; no copiar su clave a informes ni capturas.

## Arquitectura implementada y probada

- VPC personalizada y subred `10.30.1.0/24`; las VPC GCP no reciben un CIDR global.
- VM `nexoandes-gcp-standby`, e2-micro de CPU compartida y 1 GB de RAM.
- Discos estándar: 10 GB de arranque y 20 GB de datos independiente, con protección de destrucción en Terraform.
- PostgreSQL 15 como réplica por IPsec strongSwan; promoción manual y retorno a AWS probados con cinco filas sintéticas preservadas.
- Portal alternativo y sonda `/health`. El cambio de URL es manual; no hay DNS failover automático.
- Cloud Storage privado/versionado para copias, con retención configurada. Copias por HTTPS desde el equipo local y restauración probada.
- SSH con clave y orígenes administrativos acotados; la administración automatizada usa el gateway AWS. No hay 5432 público.

## Operación y límites

`./nexoandes continuidad` prepara la demostración y reconcilia las IP que cambian. `./nexoandes apagar` **detiene la misma VM y conserva los discos**; ya no elimina la instancia al apagar. La réplica detenida no recibe cambios.

Presupuesto declarado: US$10 mensuales de créditos de desarrollador. La capa gratuita está sujeta a sus condiciones; IPv4, almacenamiento, operaciones y otras cargas pueden consumir crédito. La consulta de saldo por Cloud Billing no se completó porque esa API no estaba habilitada; no se presenta crédito restante como verificado.

El portal GCP usa HTTP en esta demostración; no se declara seguridad de producción ni capacidad para miles de usuarios. La administración independiente mediante consola/IAP y el failover automático quedan fuera de las pruebas realizadas.

[Estado final y evidencias](../diagramas/excalidraw/ESTADO_2026-11-04.md) · [Operación](../integracion/CONTINUIDAD.md) · [Avances](AVANCES.md) · [Terraform](terraform/README.md).

## IAM básico — 05/11/2026

[Identidades, permisos y evidencia](../integracion/IAM.md): cinco perfiles EC2 con LabRole/IMDSv2; asignación Azure Storage Blob Data Contributor al contenedor de respaldos y copia con Entra ID; permisos de la cuenta de servicio GCP comprobados. Se conserva el privilegio administrativo heredado de los laboratorios; MFA no se afirma verificado.
