# AWS Academy

**Supabase implementado:** [acceso y pruebas](../integracion/SUPABASE.md), EC2 privada dedicada y Auth integrado al portal y Studio externo autenticado por HTTPS 8443. Estado actual activo; las notas de apagado anteriores conservan su fecha.

**Actualización V2 — 04/11/2026:** consultar el [estado con evidencias](../diagramas/excalidraw/ESTADO_2026-11-04.md) y la [guía de continuidad](../integracion/CONTINUIDAD.md). Las pruebas se distinguen del estado de apagado final.

El **22/10/2026** se desplegó con Terraform la arquitectura en la cuenta actual `849533029543`, región `us-east-1`, que estaba vacía en el inventario inicial. Se comprobaron portal HTTP 200, respaldo/restauración PostgreSQL y apagado/reencendido con los mismos datos. El estado final y las pruebas están en [evidencias actuales](evidencias/terraform-20261022/README.md).

Las pruebas del 30/09 y 01/10/2026 corresponden a la cuenta anterior `669186512136`, cuyo estado actual no se ha verificado. Conservamos el [diagnóstico inicial del cambio de cuenta](evidencias/acceso-20261022T201923Z-849533029543/RESUMEN.md); no reutilices sus IDs históricos para operar el despliegue actual.

## Mapa

- [Terraform](terraform/README.md) y [control multicloud](../infraestructura/README.md): nuevo mecanismo elegido para administrar esta cuenta; `./nexoandes panel`, `encender` y `apagar` desde la raíz.
- [README-LEARNER-LAB.md](README-LEARNER-LAB.md): README del laboratorio proporcionado por el usuario; acceso a consola, CLI y SSH, servicios admitidos, límites y presupuesto (actualización original: 24/06/2025).
- [ACCESO.md](ACCESO.md): credenciales temporales de Vocareum, SSH y comandos de comprobación.
- [AVANCES.md](AVANCES.md): estado verificado del portal AWS V1 y pendientes.
- [DESPLIEGUE_ENTREGABLE1.md](DESPLIEGUE_ENTREGABLE1.md): comprobación y actualización del portal V1.
- `infraestructura/publicar-portal.sh NUMERO_EQUIPO`: publica la página en instancias actuales y Launch Template tras verificar la cuenta y asociación del ASG.
- [infraestructura/](infraestructura/): scripts Bash, política IAM de referencia e IDs registrados en `infra-params.env`.
- `privado/`: clave SSH local; se excluye de repositorios y entregables.

## Arquitectura documentada

VPC `10.10.0.0/16`, dos subredes públicas, dos subredes privadas para aplicaciones, una subred privada de base de datos, NAT, ALB, ASG con Apache, PostgreSQL en EC2, S3 y alarmas CloudWatch. Esta lista proviene de `HISTORIAL.md`; comprueba los recursos antes de usarlos como evidencia actual.

Los scripts `deploy-infra.sh` y `deploy-ec2.sh` crean recursos y no son idempotentes. Úsalos solo después de revisar la cuenta y el inventario. `start-lab.sh` intenta reactivar recursos existentes.

## IAM básico — 05/11/2026

[Identidades, permisos y evidencia](../integracion/IAM.md): cinco perfiles EC2 con LabRole/IMDSv2; asignación Azure Storage Blob Data Contributor al contenedor de respaldos y copia con Entra ID; permisos de la cuenta de servicio GCP comprobados. Se conserva el privilegio administrativo heredado de los laboratorios; MFA no se afirma verificado.
