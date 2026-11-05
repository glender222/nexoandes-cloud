# Azure

**Actualización V2 — 04/11/2026:** consultar el [estado con evidencias](../diagramas/excalidraw/ESTADO_2026-11-04.md) y la [guía de continuidad](../integracion/CONTINUIDAD.md). Las pruebas se distinguen del estado de apagado final.

El 22/10/2026 se verificó la suscripción Azure for Students `1db87b28-407f-41d3-b532-41942343157c` y se desplegaron seis recursos Terraform en `northcentralus`: grupo, red, GatewaySubnet, almacenamiento privado/versionado, contenedor y política de retención. Azure está habilitada en el control común. VPN Gateway y Log Analytics permanecen deshabilitados. Consulta [avances](AVANCES.md) y [evidencias actuales](evidencias/terraform-20261022/README.md).

- [ACCESO.md](ACCESO.md): iniciar sesión, seleccionar suscripción y comprobar permisos.
- [AVANCES.md](AVANCES.md): estado, decisiones y próximos pasos.
- [Terraform](terraform/README.md): red, Blob y gateway/monitoreo opcionales, administrados desde el [control común](../infraestructura/README.md).
- `infraestructura/`: ubicación futura del código de red, cómputo y almacenamiento.
- `privado/`: configuración local de la CLI y otros archivos sensibles; no va en entregables.

Azure conserva una copia de respaldo; el diseño de monitoreo y conectividad entre nubes se detalla en [integracion/README.md](../integracion/README.md). El despliegue no demuestra por sí mismo replicación ni VPN.

## IAM básico — 05/11/2026

[Identidades, permisos y evidencia](../integracion/IAM.md): cinco perfiles EC2 con LabRole/IMDSv2; asignación Azure Storage Blob Data Contributor al contenedor de respaldos y copia con Entra ID; permisos de la cuenta de servicio GCP comprobados. Se conserva el privilegio administrativo heredado de los laboratorios; MFA no se afirma verificado.
