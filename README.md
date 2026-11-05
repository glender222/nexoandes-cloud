# Proyecto multicloud: AWS Academy, Azure y Google Cloud (GCP)

Este espacio reúne el desarrollo técnico del proyecto de Cloud Computing en AWS Academy, Azure y Google Cloud (GCP). Las tres nubes forman parte del objetivo final (GCP reemplaza a OCI por decisión del 28/10/2026; su acceso se verificó el 04/11/2026). El Entregable 1 trata del diseño y la implementación inicial de una arquitectura Cloud V1.

El [mapa editable y las bibliotecas de Excalidraw](diagramas/excalidraw/README.md) se mantienen en `diagramas/excalidraw/` para revisar juntos la arquitectura y su avance por entregable.

**Continuidad V2 — 04/11/2026:** [operación y pruebas](integracion/CONTINUIDAD.md), [diseño](diagramas/excalidraw/DISENO_V2.md) y [estado con evidencias](diagramas/excalidraw/ESTADO_2026-11-04.md). Este estado distingue implementación, pruebas fechadas y apagado final; las notas anteriores conservan su fecha histórica.

**Supabase activo — 04/11/2026 21:55:** [instalación, acceso y pruebas](integracion/SUPABASE.md). Supabase es el servicio SaaS académico elegido; Auth está integrado al portal AWS; la base PostgreSQL original permanece separada. El panel administrativo tiene acceso externo autenticado por HTTPS 8443 y acceso alternativo SSM; la VM GCP sigue detenida.

## Continuidad con Terraform — 22/10/2026 y actualización 28/10/2026

El usuario eligió continuar en la cuenta AWS `849533029543` y administrar las tres nubes con Terraform. El [control multicloud](infraestructura/README.md) ofrece un panel local y los comandos `./nexoandes encender` y `./nexoandes apagar`. El apagado conserva bases de datos y respaldos y retira servicios temporales; el almacenamiento puede seguir generando consumo.

AWS y Azure están habilitadas y desplegadas realmente. AWS superó el ciclo encender/apagar/reencender conservando datos; se comprobó una copia del respaldo PostgreSQL de S3 a Azure Blob mediante descarga y SHA256. Google Cloud (GCP) reemplaza a OCI. El 04/11/2026 se verificó su acceso y se implementaron réplica PostgreSQL, disco persistente y portal de contingencia; la promoción y el retorno a AWS se probaron con datos sintéticos. OCI se conserva archivado en `oci/` para referencia histórica.

## Documentación y cierre por unidad

Los informes V1/V2 y la revisión de rúbricas se actualizaron el 04/11/2026 con las pruebas reales, incluido Studio externo. La [tabla de pendientes](entregables/ESTADO_RUBRICAS.md) distingue evidencia que tomará el usuario, implementación faltante y mejoras futuras. [Guía de fotos V1](entregables/entregable-01/evidencias/README.md) · [Guía de fotos V2](entregables/entregable-02/GUIA_CAPTURAS.md). El [modelo de costos](entregables/costos/estimacion.json) es un subtotal preliminar AWS con hipótesis y exclusiones, no costo total ni saldo de crédito.

## Alcance del Entregable 1

La [plantilla oficial disponible](referencias/plantilla.docx) pide comparar al menos dos proveedores, seleccionar y justificar uno principal, presentar la arquitectura y demostrar con evidencias una solución inicial funcional. La [rúbrica](referencias/rubrica%20entregable%201.md) evalúa también el problema, los requerimientos, la red, la seguridad, la escalabilidad y los puntos únicos de falla.

Para la V1 se eligió **AWS Academy**: el portal informativo de NexoAndes ya se publicó y respondió HTTP 200 mediante el ALB. **Azure y GCP** aparecen en la comparación de proveedores y pertenecen al proyecto final multicloud. La implementación multicloud posterior se registra fuera del informe V1 y en el seguimiento del Entregable 2. El Entregable 1 requiere implementación y evidencias de la V1, no solo un diseño.

El [INFORME.md](entregables/entregable-01/INFORME.md) es el **texto fuente en Markdown** que el usuario convertirá después a Word o al formato presentable de entrega. Mantiene las 20 secciones de la plantilla y espacios para capturas. El [README del Entregable 1](entregables/entregable-01/README.md) guarda el estado y las tareas pendientes fuera del texto del informe.

## Empieza aquí

1. Lee [AGENTS.md](AGENTS.md) si vas a continuar el trabajo como agente.
2. Revisa el [estado de AWS](aws/README.md), [Azure](azure/README.md) y [GCP](gcp/README.md) (y el histórico [OCI](oci/README.md)).
3. Usa el `ACCESO.md` de la nube que necesitas y confirma la identidad antes de hacer cambios.
4. Consulta el [registro único de incidencias](incidencias/REGISTRO.md) antes de diagnosticar un fallo.
5. Para preparar el documento académico, abre la [guía del Entregable 1](entregables/entregable-01/README.md), el [texto del informe](entregables/entregable-01/INFORME.md) y las [referencias originales](referencias/README.md).



## Convención de trabajo

Cada nube tiene una guía de acceso y un registro de avances. `AVANCES.md` distingue **verificado**, **documentado históricamente** y **pendiente**. Los fallos van una sola vez al registro central con un ID que se cita desde los avances. Las evidencias de pruebas deben indicar fecha, comando o procedimiento, resultado y nube.

Los archivos en `privado/` son material local de autenticación. No copies claves, contraseñas ni tokens a Markdown, capturas o entregables. La clave SSH académica existente se conservó en `aws/privado/`; compartir esa carpeta expone el acceso asociado.

## IAM básico — 05/11/2026

[Identidades, permisos y evidencia](integracion/IAM.md): cinco perfiles EC2 con LabRole/IMDSv2; asignación Azure Storage Blob Data Contributor al contenedor de respaldos y copia con Entra ID; permisos de la cuenta de servicio GCP comprobados. Se conserva el privilegio administrativo heredado de los laboratorios; MFA no se afirma verificado.
