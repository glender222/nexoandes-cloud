Actúa como arquitecto cloud. Crea el archivo `integracion/CONTRATO.md`: el contrato que compartirán los tres agentes (AWS, Azure y OCI) para que sus trabajos encajen sin pisarse.

## Contexto del diseño (léelo completo antes de escribir)

- **Proyecto:** NexoAndes, "Proyecto Integrador" de Cloud Computing (UPeU, Ingeniería de Sistemas). Entregable 1 = diseño y documentación; Entregable 2 = seguridad, optimización, escalabilidad y resiliencia (Arquitectura V2), con implementación y evidencias.
- **Arquitectura objetivo histórica: multicloud AWS + Azure + OCI.** El editable de trabajo, que ya incorpora GCP, está en [diagramas/excalidraw/nexoandes-multicloud.excalidraw](../diagramas/excalidraw/nexoandes-multicloud.excalidraw). Este prompt conserva el contexto anterior con OCI; no inventes el diagrama ni tomes este contexto histórico como prueba de implementación.
- **Cuentas y límites (todo el diseño debe respetarlos):**
  - **AWS Academy Learner Lab:** sesiones de 4 h, credenciales temporales que cambian en cada sesión, solo el rol LabRole / LabInstanceProfile (no se crean usuarios IAM), presupuesto de USD 50–100 según el curso, ≤ 9 instancias, EC2 de nano a large, EBS ≤ 100 GB, RDS no usado. **La Site-to-Site VPN no figura en la lista de servicios que revisé: hay que probar si se puede crear una Virtual Private Gateway.** La VPN gestionada cuesta USD 0.05 por hora y por conexión. Plan B: strongSwan en una EC2.
  - **Azure for Students:** USD 100 de crédito por 12 meses, sin tarjeta; no cubre ExpressRoute, Azure DevOps ni Marketplace; los créditos de cada mes no se acumulan; con 90 días sin uso pueden borrar recursos de cómputo; el VPN Gateway cobra por hora (precio del SKU por confirmar en la calculadora).
  - **OCI Always Free, gasto cero (no se gasta ni un sol):** solo recursos listados como Always Free: VM Ampere A1 (hasta 2 OCPU y 12 GB), 200 GB de bloque (arranque + volúmenes, solo región home), 20 GB de Object Storage (50 000 peticiones/mes), 2 VCN, Bastion, Monitoring, Notifications, 10 TB de salida/mes. **No se usan DRG, CPE, Alarms ni IP pública reservada** (no constan como Always Free). Las instancias con CPU, red y memoria < 20 % durante 7 días pueden ser reclamadas. No se hace "Upgrade to Pay As You Go".
- **Direccionamiento propuesto:** AWS VPC 10.10.0.0/16 (públicas 10.10.1.0/24 y 10.10.2.0/24; app privadas 10.10.11.0/24 y 10.10.12.0/24; datos 10.10.20.0/24), Azure VNet 10.20.0.0/16, OCI VCN 10.30.0.0/16 (subred 10.30.1.0/24).
- **Estado real de AWS (verificado el 30/09/2026):** VPC, ALB (HTTP 80) con Target Group y 2 destinos saludables, Auto Scaling Group mín. 2 / máx. 4 / deseado 2 con EC2 Apache en us-east-1a y us-east-1b (subredes privadas), NAT Gateway, EC2 PostgreSQL 15 primario en una sola zona (subred de datos, volumen EBS), Security Groups (SG-ALB, SG-App, SG-DB), bucket S3 con 0 objetos, 2 alarmas de CloudWatch (disparo no probado). Conectividad TCP 5432 desde las apps a la BD probada.
- **Brechas conocidas:** respaldos reales y restauración (S3 vacío), HTTPS (hoy solo HTTP 80), SSH público por restringir, manejo de secretos, prueba de reemplazo y escalado del ASG, disparo de alarmas, la base de datos es SPOF (una sola zona), evidencias fotográficas E01–E05 y número de equipo pendientes.
- **Diseño previsto (NO desplegado) en Azure y OCI:**
  - OCI: VM Ampere A1 con réplica de PostgreSQL (misma versión mayor que el primario), strongSwan como extremo IPsec dentro de la VM (IP pública efímera, NSG con UDP 500/4500 solo desde AWS, SSH solo por Bastion), Object Storage como copia 1 de respaldos, Monitoring.
  - Azure: VNet, VPN Gateway, Blob Storage (LRS, nivel cool) como copia 2 de respaldos, Azure Monitor, Cost Management con alertas al 50 % y 80 % de los USD 100.
  - Interconexión: IPsec site-to-site con la Virtual Private Gateway de AWS como centro (VPN #1 AWS↔Azure, VPN #2 AWS↔OCI).
- **Reglas de honestidad (obligatorias):** nunca marques algo como "implementado" sin evidencia verificable; Azure y OCI figuran como "diseño previsto" hasta que existan de verdad; si un dato no lo conoces, escribe `POR VERIFICAR`, no lo inventes; no atribuyas a la V1 pruebas que no se hicieron.
- **Secretos:** nunca escribas contraseñas, claves, PSK, tokens ni credenciales en ningún archivo versionado. Si hace falta referirse a uno, escribe "ver `privado/`". La carpeta `privado/` no se versiona.
- **Estructura del repo:** `aws/`, `azure/`, `oci/` (cada una con `infraestructura/`, `privado/`, `ACCESO.md`, `AVANCES.md`, `README.md`), `entregables/entregable-01/`, `entregables/entregable-02/`, `integracion/`.


## Qué debe contener `integracion/CONTRATO.md`
1. **Propósito y reglas de cambio.** Es la única fuente de verdad de lo compartido. Ningún agente cambia un valor aquí sin dejar una entrada en el registro de decisiones (sección 9) y avisarme.
2. **Direccionamiento.** Tabla por nube: red, CIDR, subredes, función. Comprueba que no haya solapamientos y que quede espacio de crecimiento.
3. **Valores compartidos.** Tabla con columnas: nombre, quién lo produce, quién lo consume, dónde se guarda (documento público o `privado/`), estado. Incluye como mínimo: IP pública de la VM de OCI, ID de la Virtual Private Gateway y de las conexiones VPN en AWS, IP pública del VPN Gateway de Azure, IP de salida (NAT) de AWS, claves precompartidas de los túneles (solo "ver `privado/`"), nombre de los buckets/contenedores de respaldo.
4. **Matriz de flujos de red permitidos.** Origen → destino → protocolo/puerto → motivo. Incluye UDP 500/4500 y ESP si hace falta, TCP 5432 solo desde la subred 10.30.1.0/24 hacia la BD primaria, SSH solo por Bastion/rutas definidas, HTTP/HTTPS. Todo lo demás, denegado.
5. **Convenciones.** Nombres de recursos, etiquetas/tags obligatorias (`proyecto=nexoandes`, `nube`, `estado`, `responsable`) y formato de las evidencias (códigos E06 en adelante).
6. **Replicación de PostgreSQL.** Requisitos (no secretos): versión mayor idéntica, método (streaming con slot de replicación), TLS, usuario de replicación dedicado, qué se reemplica, cómo se verifica el retraso, y procedimiento manual de promoción de la réplica en OCI.
7. **Respaldos (regla 3 copias).** Copia local/AWS S3 (hoy 0 objetos), copia 1 en OCI Object Storage (límite 20 GB: define retención y rotación para no pasarte), copia 2 en Azure Blob. Cifrado, frecuencia, prueba de restauración, y **decisión abierta**: cómo llega el respaldo a Blob y a Object Storage (por el túnel o por el endpoint público con firewall e identidad mínima) — propón una opción con ventajas y costos y déjala como pendiente de mi confirmación.
8. **Metas de resiliencia.** Propón RPO y RTO realistas para este laboratorio, marcadas como "propuesta por validar", y explica qué falla cubre cada una.
9. **Registro de decisiones y preguntas abiertas.** Fecha, decisión, motivo, quién decidió.
10. **Riesgos de integración.** En especial: Site-to-Site VPN no confirmada en el Learner Lab (Plan B con strongSwan), IP efímera de la VM de OCI (no eliminar la VM), costo por hora de las VPN, reclamo por inactividad en OCI, caducidad de credenciales de AWS.

Si falta información para algún valor, déjalo como `POR VERIFICAR` con el nombre del agente que debe producirlo.

## Reglas para esta tarea
- **Solo escribes archivos Markdown.** No ejecutes comandos contra ninguna nube, no crees ni borres recursos.
- Escribe en español, con tablas donde ayuden a comparar y listas de tareas donde haya pasos.
- Antes de escribir, **lee los archivos existentes** que se indican y apóyate en ellos; si contradicen este contexto, no elijas: anótalo en la sección "Discrepancias" del archivo.
- Cada tarea del plan debe poder verificarla otra persona: acción concreta, criterio de aceptación medible y evidencia que se guarda.
- Marca con `[HUMANO]` lo que solo puede hacer yo (registros, aceptar términos, MFA, capturas de pantalla reales, cualquier decisión de gasto) y con `[AGENTE]` lo que puede hacer un agente de Claude Code.
- Al terminar, muéstrame: (1) la ruta del archivo, (2) un resumen de 5 líneas, (3) la lista de preguntas abiertas y de datos marcados `POR VERIFICAR`.

Antes de escribir, lee `aws/ACCESO.md`, `aws/AVANCES.md`, `aws/DESPLIEGUE_ENTREGABLE1.md` y `entregables/entregable-01/INFORME.md` si existen (sin copiar ningún secreto).
