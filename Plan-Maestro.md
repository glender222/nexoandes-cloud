Actúa como líder técnico del proyecto. Crea el archivo `PLAN-MAESTRO.md` en la raíz del repo: el plan general que coordina a los tres agentes de nube y que sirve de guía para el Entregable 2.

## Contexto del diseño (léelo completo antes de escribir)

- **Proyecto:** NexoAndes, "Proyecto Integrador" de Cloud Computing (UPeU, Ingeniería de Sistemas). Entregable 1 = diseño y documentación; Entregable 2 = seguridad, optimización, escalabilidad y resiliencia (Arquitectura V2), con implementación y evidencias.
- **Arquitectura objetivo histórica: multicloud AWS + Azure + OCI.** El editable de trabajo, que ya incorpora GCP, está en [diagramas/excalidraw/nexoandes-multicloud.excalidraw](diagramas/excalidraw/nexoandes-multicloud.excalidraw). Este prompt conserva el contexto anterior con OCI; no inventes el diagrama ni tomes este contexto histórico como prueba de implementación.
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


## Qué debe contener `PLAN-MAESTRO.md`
1. **Objetivo y alcance.** Qué es la V1 (portal informativo de catálogo, ya en AWS), qué agrega el Entregable 2 y qué queda fuera (pedidos, inventario transaccional, funciones entre nubes que no se puedan probar).
2. **Diagrama y estado por nube.** Inserta o enlaza el diagrama y una tabla de estado: nube, componentes, estado (implementado / diseño previsto / bloqueado), evidencia.
3. **Fases con puertas de paso (gates).**
   - **Fase 0 · Viabilidad:** crear una Virtual Private Gateway en el Learner Lab; comprobar capacidad de la VM Ampere A1 en la región home de OCI (si no hay, definir plan B con AMD micro); confirmar el precio del VPN Gateway de Azure y el SKU mínimo. Si una falla, qué se cambia en el diseño antes de seguir.
   - **Fase 1 · Módulos en paralelo:** AWS, OCI y Azure, cada uno hasta antes de la VPN.
   - **Fase 2 · Integración:** túneles VPN, replicación de PostgreSQL, respaldos.
   - **Fase 3 · Pruebas y evidencias:** caída de zona, reemplazo de instancia del ASG, restauración desde respaldo, promoción de la réplica, disparo de alarmas.
   Para cada fase: entradas, salidas, criterio de salida y qué módulo depende de cuál.
4. **Reparto de agentes.** Un agente por nube (`aws/PLAN.md`, `azure/PLAN.md`, `oci/PLAN.md`), qué carpeta puede editar cada uno y cómo se coordinan solo a través de `integracion/CONTRATO.md`.
5. **Reglas globales para agentes** (esta sección se copiará luego a `CLAUDE.md`): cada agente edita solo su carpeta; nada de secretos en archivos versionados; preguntar antes de crear algo que cobre; no marcar "implementado" sin evidencia; actualizar `AVANCES.md` al terminar cada tarea; usar siempre la etiqueta `POR VERIFICAR` en vez de inventar; al empezar una sesión de AWS, renovar credenciales y verificar el estado antes de actuar.
6. **Control de costos.** Presupuesto por nube (AWS: según el curso, USD 50–100; Azure: USD 100; OCI: USD 0), alertas, rutina de apagado/borrado de lo que cobra por hora (VPN), y quién revisa el gasto y cuándo.
7. **Mapa hacia la rúbrica del Entregable 2.** Tabla con los 5 criterios (evolución V1→V2; amenazas y vulnerabilidades; controles de seguridad; escalabilidad, disponibilidad y tolerancia a fallos; evidencias y documentación) y, para cada uno, qué tareas de los planes lo respaldan y qué evidencia lo demuestra.
8. **Lista de evidencias.** Códigos E06 en adelante con qué muestran, quién las captura y de qué tarea salen. Las capturas son reales y las hago yo; nunca se simulan.
9. **Matriz de amenazas inicial.** Amenaza, activo, control previsto, estado. Debe incluir SSH público, HTTP sin cifrar, secretos, BD en una sola zona, pérdida de respaldos, credenciales caducadas, reclamo de la VM de OCI, cobro inesperado.
10. **Registro de riesgos y plan B**, y **definición de terminado** para el Entregable 2.
11. **Cronograma sugerido** en bloques de trabajo (sin fechas inventadas; pon "fecha de entrega: POR VERIFICAR").

## Reglas para esta tarea
- **Solo escribes archivos Markdown.** No ejecutes comandos contra ninguna nube, no crees ni borres recursos.
- Escribe en español, con tablas donde ayuden a comparar y listas de tareas donde haya pasos.
- Antes de escribir, **lee los archivos existentes** que se indican y apóyate en ellos; si contradicen este contexto, no elijas: anótalo en la sección "Discrepancias" del archivo.
- Cada tarea del plan debe poder verificarla otra persona: acción concreta, criterio de aceptación medible y evidencia que se guarda.
- Marca con `[HUMANO]` lo que solo puede hacer yo (registros, aceptar términos, MFA, capturas de pantalla reales, cualquier decisión de gasto) y con `[AGENTE]` lo que puede hacer un agente de Claude Code.
- Al terminar, muéstrame: (1) la ruta del archivo, (2) un resumen de 5 líneas, (3) la lista de preguntas abiertas y de datos marcados `POR VERIFICAR`.

Antes de escribir, lee `integracion/CONTRATO.md` (debe existir), `entregables/entregable-01/INFORME.md`, `entregables/entregable-01/REVISION_RUBRICA.md` y `entregables/entregable-02/README.md` si existen. No contradigas el contrato: si necesitas cambiar algo, anótalo como propuesta.
