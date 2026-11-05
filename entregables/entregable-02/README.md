# Entregable 2 — preparación de la Arquitectura V2

Documento fuente: [INFORME.md](INFORME.md). Conservar la estructura de la plantilla oficial; este README contiene seguimiento y no pertenece al documento final.

## Estado técnico del 04/11/2026

El [estado con evidencias](../../diagramas/excalidraw/ESTADO_2026-11-04.md) y el [diseño V2](../../diagramas/excalidraw/DISENO_V2.md) sustituyen las suposiciones anteriores. El editable está en [diagramas/excalidraw](../../diagramas/excalidraw/README.md).

- AWS: portal entre dos zonas, ASG 2–4, PostgreSQL privado persistente, S3, IPsec y HTTPS académico.
- Azure: Blob privado/versionado como copia independiente; no se afirma inmutabilidad ni VPN activa.
- GCP: réplica PostgreSQL y portal de contingencia en e2-micro, con datos en disco independiente. Detener conserva datos; no se garantiza costo cero.
- Copias entre nubes por HTTPS, coordinadas desde el equipo local. La réplica usa IPsec.

**Ampliación Supabase del 04/11/2026:** Auth y acceso privado del portal implementados sobre una EC2 AWS dedicada. Login, rechazo sin token, logout, reinicio y bootstrap de una web del ASG probados; backup propio en tres nubes y restauración selectiva de usuarios verificada. Supabase se documenta como backend open source sobre IaaS; se presenta como nuestro SaaS académico; no acredita por sí solo un producto comercial completo ni failover de identidad. Studio externo HTTPS 8443 autenticado se publicó y probó a las 23:33. [Guía y evidencias](../../integracion/SUPABASE.md).

## Pruebas y límites

| Prueba | Evidencia del ensayo |
|---|---|
| Acceso web y datos | HTTP 200 en AWS/GCP y lectura de tabla sintética; HTTPS AWS verificado con certificado propio |
| Seguridad | Conexión desde fuente no autorizada a PostgreSQL bloqueada; SSH GCP restringido; secretos fuera de evidencias |
| Fallo web | Instancia terminada, reposición y dos destinos saludables en 229,79 s; 183 respuestas HTTP 200, cero errores observados |
| Escalabilidad | Crecimiento automático 2→4 por solicitudes; 2137 respuestas HTTP 200. La prueba CPU quedó limitada por créditos T3 y no se presenta como éxito |
| Recuperación | Réplica, promoción manual GCP, escritura y retorno a AWS; cinco filas sintéticas coincidentes. Restauración en GCP desde las copias descargadas de Azure y GCP |

El ensayo midió 7,87 s hasta BD GCP disponible y 24,66 s hasta reconexión de la aplicación AWS. No son un SLA ni un RPO universal. El acceso alternativo usa otra URL manual; no se probó caída real del proveedor ni de su plano de administración. Los servidores web nuevos deben reconciliar la sonda; la reposición del portal estático se prueba por separado.

## Actualización documental del 04/11/2026

Se reescribieron las secciones manteniendo sus títulos y orden. Se corrigieron afirmaciones de inmutabilidad, 5.000 usuarios, cero costo, roles ficticios, snapshots y eliminación total de SPOF. Se incorporaron el mapa actual exportado, plan de seguridad con NIST CSF 2.0 como referencia, pruebas Supabase/Studio y costos preliminares reproducibles. No se desplegaron mejoras adicionales durante esta actualización.

La figura V1 se conserva y la V2 está en `evidencias/arquitectura-v2.png` / `.svg`; no se sustituyeron las fotos que tomará el usuario. Los datos personales/de equipo de la carátula proceden del informe anterior y se mantienen para revisión del equipo; la fecha refleja actualización técnica, no una fecha de entrega confirmada.

El [estado de rúbrica](REVISION_RUBRICA.md), la [guía de fotos](GUIA_CAPTURAS.md) y la [tabla consolidada](../ESTADO_RUBRICAS.md) indican lo que falta. IAM básico cerrado el 05/11; ver [identidades y pruebas](../../integracion/IAM.md). Prioridades: fotos/datos y cierre económico. El usuario excluyó el ensayo de restauración integral Supabase del trabajo activo el 05/11; sigue documentado como limitación, sin presentarlo como realizado. Mejoras de monitoreo, copias autónomas, acceso GCP independiente y HA/TLS se distinguen de requisitos literales.

## Documento presentable — 05/11/2026

[Word editable de la Unidad 2](Glender_Vargas_Entregable_2_Cloud_Computing.docx), elaborado sobre la plantilla oficial de Unidad 2 sin rediseño. Conserva sus 19 apartados 02–20, estilo visual, colores y estructura de evidencias. La revisión solicitada posteriormente retira cuadros de indicaciones de plantilla y amplía la arquitectura V2 en una página horizontal. Se completaron las celdas originales con contenido técnico resumido, figuras V1/V2, IAM y límites; se revisaron las páginas renderizadas. No se hicieron operaciones cloud.

La referencia válida de V1 es [el primer entregable facilitado por el usuario](../entregable-01/doc_entregale_ofivial_3f4gemu4pndm.docx), SHA256 56ece16912c77491ec5b69b292ff9410793954b073df8a39a568b6c6e93bd285. El archivo vargas_glender_examen_cloud_j9hc2cis6qzu.docx es un examen y no define la V1 del proyecto. Se conservan nombre/código/docente del entregable correcto; Equipo XX sigue pendiente de confirmar. La figura V1 es su diagrama AWS original, extraído sin redibujarlo. Se distinguió la verificación 30/09, recreación AWS 22/10 y cambio OCI→GCP 28/10.

Para la siguiente edición, trabajar sobre el mismo Word e insertar las capturas en sus recuadros; evitar reemplazarlo por una conversión genérica del Markdown. Actualizar el índice en Word mediante clic derecho → Actualizar campo → Actualizar toda la tabla: se conserva el campo TOC original y se activó su actualización al abrir. Su resultado en caché queda pendiente del motor Word; no se reescribió el documento mediante LibreOffice.

## Corrección de presentación y fotografías — 05/11/2026

Se editó el mismo Word: seis capturas auténticas insertadas (tres del Entregable 1 y tres de pruebas del 04/11), con pies de procedencia y límites. [Procedencia de fotos V1](evidencias/capturas-v1/procedencia.json). Se retiraron los veinte cuadros de INDICACIÓN, incluido el ejemplo ASCII de arquitectura, y el flujo conceptual decorativo. Se conservaron los títulos oficiales 02–20 y el diseño azul/dorado. El diagrama V1 ocupa el ancho de su página; el V2 pasa de aproximadamente 4,5 a 8,73 pulgadas en una página horizontal con cabecera/pie adaptados.

La tabla Escalabilidad registra lo ejecutado (solicitudes, reposición y límite de CPU) y no presenta escenarios de 100–5.000 usuarios como resultados. Las fotos del portal acreditan funcionamiento y autenticación; escalado, réplica, hashes y permisos se sustentan con sus JSON, sin simular pantallas de consola. El proyecto sigue teniendo fotos específicas adicionales por tomar si se requieren: historial ASG, copias Azure/GCP e IAM. El índice conserva su campo TOC para actualizar en Word. No se operó infraestructura ni se modificó el primer entregable.

## Reservas de capturas y mapa corregido — 05/11/2026

Se actualizó la figura V2 del mismo Word con el Excalidraw corregido. Se añadieron 19 reservas R01–R19 en Seguridad, IAM, Red, Escalabilidad, Alta disponibilidad, Monitoreo, Backup, Pruebas y Costos. IAM, red, copias y costos distinguen AWS/Azure/GCP; cada reserva contiene descripción, fecha/hora y resultado por completar. Se mantienen seis fotos, los 19 títulos 02–20, estilos, cabeceras y pies. Resultado: 20 páginas revisadas, con el mapa en la página horizontal 6. Las reservas no acreditan pruebas nuevas. Actualizar el índice al abrir en Word y sustituir el párrafo “Pegar captura aquí” por la foto, conservando su pie. No se operó infraestructura.

## Formato con fotografías e índice completo — 05/11/2026

Se tomó como fuente la copia con fotos que el usuario guardó en `entregables/entregable-01/Glender_Vargas_Entregable_2_Cloud_Computing.docx`; permanece sin cambios. El Word de trabajo final está en esta carpeta de Entregable 2. Se conservaron las 33 imágenes byte a byte y los 19 títulos oficiales. Se completó el índice con 22 entradas enlazadas y números contrastados con el render; se mantiene el campo TOC para Word. Se corrigieron tabulaciones de cabecera/pie, párrafos de reserva, saltos y continuidad de tablas y fotos; los pies ahora describen la evidencia aportada sin inventar fechas. Resultado: 25 páginas renderizadas y revisadas, frente a las 35 de la fuente. La arquitectura V2 ocupa una página horizontal.

Pendientes de contenido separados del formato: Equipo XX y las dos vistas señaladas al usuario (R01 muestra Studio, R06 reglas de salida). Las fotos se conservaron y sus pies explican lo que acreditan. No se operó infraestructura ni se añadieron ensayos.
