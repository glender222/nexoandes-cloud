# Integración de NexoAndes

La guía operativa actual es [CONTINUIDAD.md](CONTINUIDAD.md). El [diseño V2](../diagramas/excalidraw/DISENO_V2.md) y el [mapa editable](../diagramas/excalidraw/nexoandes-multicloud.excalidraw) describen AWS como primario, GCP como contingencia y Azure como copia independiente.

El usuario autorizó el trabajo completo el 04/11/2026. El [estado con evidencia](../diagramas/excalidraw/ESTADO_2026-11-04.md) y las [pruebas reales](evidencias/20261104/) distinguen réplica, copias, restauración, fallos y límites. La disponibilidad actual requiere inventario: un estado Terraform o una prueba histórica no la sustituyen.

AWS usa 10.10.0.0/16; Azure 10.20.0.0/16; GCP usa la subred 10.30.1.0/24 en una VPC personalizada. La réplica usa IPsec y los respaldos HTTPS. No hay conmutación DNS automática.

`CONTRATO.md`, `Plan-Maestro.md` y `referencias/oficial/DISEÑO.md` conservan prompts/diseños anteriores con OCI; no son instrucciones operativas del despliegue actual. OCI está archivada. Los informes académicos y sus capturas se preparan por entregable y unidad.

**Supabase — implementado el 04/11/2026:** [instalación, acceso y pruebas](SUPABASE.md). Autohospedaje open source en EC2 privada dedicada, Auth integrado al portal y respaldo propio. `./nexoandes supabase` reproduce el arranque AWS; `./nexoandes apagar` conserva los datos.

## IAM básico — 05/11/2026

[Identidades, permisos y evidencia](IAM.md): cinco perfiles EC2 con LabRole/IMDSv2; asignación Azure Storage Blob Data Contributor al contenedor de respaldos y copia con Entra ID; permisos de la cuenta de servicio GCP comprobados. Se conserva el privilegio administrativo heredado de los laboratorios; MFA no se afirma verificado.
