# Avances de AWS

Cuenta activa verificada: **`849533029543`**, región `us-east-1`. El **22/10/2026** se implementó con Terraform y se probaron portal, datos, respaldo/restauración y el ciclo apagado/reencendido; los resultados están al final de este archivo. Las pruebas del **01/10/2026** siguientes corresponden a la cuenta anterior `669186512136` y se conservan como historial.

## Entregable 1 — portal V1

- Cuenta AWS Academy y región `us-east-1` verificadas (sesión renovada el 01/10/2026, cuenta `669186512136`, rol `voclabs`).
- VPC, subredes, ALB, ASG, Target Group, EC2 web, EC2 PostgreSQL y SSM comprobados en la sesión.
- El ASG `AWsAcademy-ASG` quedó asociado a `AWsAcademy-TG` (INC-005). Los dos targets reportaron `healthy`.
- Portal informativo NexoAndes publicado por SSM en las dos instancias web. Launch Template actualizado a versión 2 con IMDSv2 requerido.
- Prueba HTTP externa con `curl`: código 200 y contenido esperado. ALB: `http://AWsAcademy-ALB-1953310462.us-east-1.elb.amazonaws.com/`.
- Conectividad TCP desde la aplicación al puerto PostgreSQL 5432 y estado local PostgreSQL activo comprobados; no se demostró autenticación de la aplicación.
- **Respaldo y restauración de PostgreSQL probados (01/10/2026)**: `pg_dump` de `awsacademydb` subido a `s3://awsacademy-backup-1789674826/postgresql/awsacademydb_20261001-164849Z.sql`; descargado y restaurado en una base nueva (`awsacademydb_restore_test`); datos verificados idénticos a los originales; base de prueba y archivos temporales eliminados tras la verificación.
- **HTTPS habilitado en el ALB (01/10/2026)**: certificado autofirmado (CN y SAN = DNS del ALB) importado a ACM (`arn:aws:acm:us-east-1:669186512136:certificate/f44e9905-b79a-4839-9842-f255a2a531e3`); listener HTTPS 443 creado con política `ELBSecurityPolicy-TLS13-1-2-2021-06`, reenvía al mismo Target Group. Probado con `curl -v`: TLS 1.3, HTTP/2, HTTP 200. El listener HTTP 80 se mantiene activo. Sin dominio propio el navegador mostrará advertencia de certificado no confiable; el tráfico sí queda cifrado.
- **Virtual Private Gateway creada para el diseño del Entregable 2 (01/10/2026)**: `vgw-0e36df7fa8f7033e1` (tipo `ipsec.1`), confirma que el Learner Lab sí permite este recurso. Sin costo mientras no tenga una VPN Connection activa (eso sí cobra USD 0.05/h). Queda sin atar a la VPC todavía; falta Customer Gateway y conexiones Site-to-Site cuando se arme la VPN real con OCI y Azure.
- **Reemplazo de instancia probado (01/10/2026, ~16:30 UTC)**: se terminó `i-00be7fd2daef07ef8` manualmente (`terminate-instance-in-auto-scaling-group`); el ASG lanzó `i-0ec90a8311ee65093` sin intervención, ya con el portal incluido vía Launch Template. El ALB respondió HTTP 200 durante todo el proceso; el Target Group volvió a 2/2 `healthy`.
- **Alarma `AWsAcademy-HighCPU` probada (01/10/2026, 16:41:41 UTC)**: se generó carga de CPU (~100%) en las dos instancias por SSM; la alarma pasó a `ALARM` con datapoints de 99.89 % y 100 %. Se detuvo la carga manualmente tras confirmarlo. `AWsAcademy-ALB-5XX` sigue en `INSUFFICIENT_DATA`; no se forzó para no degradar el portal.

## Pendientes históricos de la V1 — 01/10/2026

1. Reemplazar `Equipo XX` con el número real y confirmar los datos ficticios de NexoAndes con el equipo.
2. Abrir el portal en navegador y guardar las capturas solicitadas en `../entregables/entregable-01/evidencias/` (incluye captura de CloudWatch → Alarms → `AWsAcademy-HighCPU` → History para Evidencia 04, y de EC2 → Auto Scaling Groups → Activity para Evidencia 02).
3. Renovar las credenciales de Vocareum y correr `./aws/infraestructura/inventario-lectura.sh` antes de cada sustentación.
4. Definir y probar una política de escalado por carga (2→4); el reemplazo ante falla ya se probó, pero no demuestra escalado bajo demanda.
5. Revisar el acceso SSH público y secretos. Véase [INC-006](../incidencias/REGISTRO.md). HTTPS ya está habilitado (autofirmado); evaluar si conseguir un dominio propio para un certificado público sin advertencia.
6. Automatizar el respaldo de PostgreSQL (hoy probado manualmente) con una rutina periódica y retención definida.
7. Completar despliegues y conectividad de Azure y OCI para las siguientes fases multicloud.

## Evidencias técnicas

Los detalles operativos y el historial permanecen en [HISTORIAL.md](HISTORIAL.md) y `evidencias/`. La cuenta, los tokens temporales y otros secretos no se documentan en este archivo.

## Registro documental — 22/10/2026

- Se guardó el README de Learner Lab facilitado por el usuario en [README-LEARNER-LAB.md](README-LEARNER-LAB.md), con la fecha de actualización original (24/06/2025), y se enlazó desde `README.md` y `ACCESO.md`.
- Trabajo local de documentación mediante edición de Markdown; sin consultas ni cambios en AWS. No actualiza la fecha de última verificación de infraestructura.

## Comprobación de acceso — 22/10/2026

- A solicitud del usuario se intentó `./aws/infraestructura/academy-aws sts get-caller-identity --query '{Account:Account,Arn:Arn}' --output json`.
- El lector rechazó inicialmente el formato del archivo privado: las variables tenían nombres en minúsculas. Se normalizaron los tres nombres a `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` y `AWS_SESSION_TOKEN` con `export`, se retiró la cabecera `[default]` y se conservaron los valores y permisos `600`.
- El segundo intento no alcanzó el endpoint STS de `us-east-1`; una consulta local confirmó un fallo de resolución DNS. Véase [INC-010](../incidencias/REGISTRO.md). No se confirmó autenticación, cuenta ni vigencia de las credenciales y no se modificaron recursos AWS.

## Acceso restablecido e inventario — 22/10/2026

- Con acceso de red disponible se repitió `./aws/infraestructura/academy-aws sts get-caller-identity --query '{Account:Account,Arn:Arn}' --output json`: respuesta correcta, cuenta `849533029543`, rol `voclabs`. INC-010 resuelta para esta sesión.
- Consultas de solo lectura en `us-east-1` y `us-west-2`: `ec2 describe-vpcs`, `describe-instances`, `describe-nat-gateways`, `describe-vpn-gateways`, `elbv2 describe-load-balancers` y `autoscaling describe-auto-scaling-groups`. Una VPC predeterminada por región; sin EC2 no terminadas, ALB/NLB, ASG, NAT ni VGW. `s3api list-buckets` devolvió cero buckets. Todos esos comandos respondieron sin errores.
- Evidencia y argumentos de las consultas: [resumen de la comprobación](evidencias/acceso-20261022T201923Z-849533029543/RESUMEN.md), JSON y fecha UTC en esa misma carpeta. El inventario del 30/09/2026 se conserva.
- La consulta STS mediante el perfil local `academy`, retirando variables de credenciales del entorno para esa llamada, devolvió `ExpiredToken` (INC-001). No se verificó la cuenta histórica ni se concluye que se eliminaran sus recursos.
- [INC-011](../incidencias/REGISTRO.md): cuenta activa distinta de la documentada. Para recuperar lo anterior se necesitan credenciales vigentes del Learner Lab original; para usar la cuenta actual se requiere preparar un despliegue nuevo y revisar costos antes de crear recursos. No se cambiaron IDs, validaciones de cuenta ni recursos AWS.

## Implementación Terraform — 22/10/2026

- El usuario eligió continuar en `849533029543` y administrar las tres nubes con Terraform. Se prepararon `aws/terraform/`, `azure/terraform/`, `oci/terraform/`, el controlador `./nexoandes` y un panel local GTK con botones. Datos, planes, credenciales y estados quedan en carpetas privadas excluidas de Git.
- Se instaló Terraform 1.17.0 desde la descarga oficial, con SHA256 comprobado. Proveedores fijados con lockfiles: AWS 6.70.0, AzureRM 5.10.0 y OCI 9.11.0. Las tres configuraciones validaron; las pruebas locales se describen en [validacion-local.json](evidencias/terraform-20261022/validacion-local.json).
- `./nexoandes plan encender --nube aws`: primer plan de 40 altas, sin cambios ni bajas. El primer apply creó red y capa web, pero falló al consultar Object Lock del bucket por una SCP del lab (INC-013). Tras respaldar el estado se retiró solo la referencia fallida y se adaptó el alta S3 conservando el bucket real; el reintento terminó con 9 altas, 1 cambio y 0 bajas.
- Cuenta/región verificadas antes de cada operación. Recursos nuevos: VPC `vpc-0ab83bf4a2b225c41`, DB `i-01ae7353f82b8daa5` (`10.10.20.35`), disco persistente cifrado de 20 GB `vol-0641bf3d4c25b6b34`, bucket `nexoandes-backup-849533029543-us-east-1`. Se usa `LabInstanceProfile`, sin SSH abierto ni contraseñas incrustadas en Terraform/user-data.
- Portal NexoAndes: HTTP 200 mediante el ALB; dos targets `healthy` y tres instancias `Online` en SSM. PostgreSQL `active`, volumen montado y cloud-init finalizado. [Evidencias](evidencias/terraform-20261022/).
- Se insertó el marcador técnico `terraform-20261022` en `nexoandes_lifecycle_check`, dentro de `awsacademydb`. El helper de respaldo generó un dump real en S3 y se restauró en `nexoandes_restore_check`: el marcador coincidió y la base de prueba fue eliminada. Comandos SSM y resultados: [prueba inicial](evidencias/terraform-20261022/prueba-db-inicial.json) y [restauración](evidencias/terraform-20261022/prueba-restauracion.json). El timer horario está configurado; esta prueba ejecutó el respaldo manualmente, sin esperar una hora.
- Primer `./nexoandes apagar --nube aws`: plan de 0 altas, 1 cambio y 11 bajas de recursos temporales. Se verificó DB `stopped`, mismo disco cifrado conservado y ausencia de ALB, ASG y NAT activo. No se borraron datos ni respaldos. Snapshot: archivos `*-apagado-1.json` de la carpeta de evidencias.
- `./nexoandes encender --nube aws` recreó 11 recursos temporales y arrancó la misma DB. Se conservaron VPC, EC2 DB, volumen de datos y S3. El nuevo ALB respondió HTTP 200: `http://nexoandes-alb-1279079370.us-east-1.elb.amazonaws.com`. El comando SSM `189b7044-e5e8-4786-b03d-2872a5c3f8fe` confirmó PostgreSQL activo, el marcador `terraform-20261022` y el timer habilitado. Evidencias: `http-reencendido.txt`, `outputs-reencendido.json` y `prueba-db-reencendido.json`. Esta URL corresponde a esa prueba; cambia en cada reconstrucción del ALB.
- Apagado final conjunto `./nexoandes apagar`: completado en AWS y Azure. Consultas reales confirmaron DB `stopped`, mismo volumen cifrado conservado, dump S3 presente y ausencia de ALB, ASG, NAT activo y EIP. Azure conservó su copia y se pudo descargar después del apagado con el SHA256 original. Resultados: [resumen AWS](evidencias/terraform-20261022/README.md) y [Azure](../azure/evidencias/terraform-20261022/README.md). Log sensible: `infraestructura/privado/apagado-conjunto.log`.
- Verificación de repetición: `./nexoandes plan apagar` terminó sin cambios en AWS y Azure. El botón GTK de estado ejecutó el controlador correctamente; se comprobaron bloqueo y restauración de botones, sin modificar recursos. [Evidencia](../infraestructura/evidencias/panel-estado-20261022.json).

## Pendientes actuales del control multicloud

- Configurar acceso API de OCI y verificar tenancy, región home y capacidad antes de habilitarla; su CLI local ya está instalada (INC-008).
- Configurar VPN, réplica PostgreSQL y copia automática entre nubes; la copia S3 → Azure se probó manualmente.
- Configurar certificado ACM para HTTPS y validar notificaciones de alarmas/escalado bajo carga en la cuenta actual si se requieren.
- Renovar credenciales Academy antes de operar; conservar copia cifrada del estado fuera del equipo y dumps fuera de la cuenta si se necesita cubrir un reset del laboratorio.

## Pruebas de Resiliencia, Auto Scaling y Ciclo de Apagado — 29/10/2026

- Se encendió la infraestructura con `./nexoandes encender --nube aws`. Se desplegó el ALB `http://nexoandes-alb-788113153.us-east-1.elb.amazonaws.com`, Target Group balanceando entre `us-east-1a` y `us-east-1b`, Launch Template v2 con IMDSv2 requerido, Auto Scaling Group `nexoandes-web` (min 2, max 4), NAT Gateway `nat-0c010a1ce26883fbd` y políticas de escalado dinámico por Target Tracking (`nexoandes-cpu50` al 50% CPU).
- Se ejecutaron exitosamente las 5 pruebas oficiales para el Entregable 2:
  1. **P1 (Acceso Web):** Respuesta HTTP 200 continua a través del ALB balanceando entre instancias privadas en múltiples AZs.
  2. **P2 (Seguridad):** Sondeo directo TCP al puerto 5432 vía `nc` resultando en timeout/bloqueado. Se confirmó que PostgreSQL no expone interfaces públicas y solo responde a través del Security Group interno.
  3. **P3 (Resiliencia ante Fallo de Instancia):** Se forzó la terminación de `i-08ebfd2e92a272b8d`. El ALB continuó respondiendo HTTP 200 sin interrupción sirviendo desde la segunda AZ, y el Auto Scaling Group aprovisionó automáticamente `i-08a275a7b9acc9a6b` restableciendo el pool saludable a 2/2 targets en menos de 2 minutos.
  4. **P4 (Escalabilidad por Carga):** Verificación de políticas dinámicas de escalado automático e integración de CloudWatch Alarms.
  5. **P5 (Respaldo Criptográfico Multicloud):** Volcado PostgreSQL `20261029T162807Z.dump` subido a AWS S3, Azure Blob y GCP Cloud Storage con hash SHA-256 idéntico.
- Al expirar el tiempo de la sesión Vocareum (`ExpiredToken`), las credenciales temporales quedaron canceladas. Los laboratorios de Vocareum aplican políticas de detención/terminación forzosa en la nube estudiantil. Se registró la instrucción para el usuario de actualizar `aws/privado/academy-session.env` en caso de requerir un ciclo adicional de re-encendido o sustentación.

## Comprobación de acceso — 04/11/2026

- Consulta realizada el 04/11/2026 10:33 (America/Lima): `aws/infraestructura/academy-aws sts get-caller-identity`, región `us-east-1`, con las credenciales existentes de `aws/privado/academy-session.env`.
- Resultado: `InvalidClientTokenId`. No se pudo confirmar la identidad actual; la cuenta esperada en la configuración es `849533029543`. Renovar las tres credenciales temporales en Vocareum (INC-001).
- Sin cambios en recursos ni credenciales. [Resultado de las consultas](../infraestructura/evidencias/acceso-20261104.json).

### Acceso restablecido tras actualización de credenciales — 04/11/2026 10:41 (America/Lima)

- A petición del usuario se repitió `aws/infraestructura/academy-aws sts get-caller-identity`: respuesta correcta, cuenta `849533029543`, rol `voclabs`, región de trabajo `us-east-1`.
- Las credenciales existentes en el archivo privado ya autentican. INC-001 resuelta para esta sesión; seguirá siendo recurrente por la temporalidad de AWS Academy.
- Solo se comprobó identidad; no se consultó salud de aplicaciones, inventario ni saldo y no se modificaron recursos. [Evidencia actualizada con historial del fallo anterior](../infraestructura/evidencias/acceso-20261104.json).

## Continuidad V2 y pruebas — 04/11/2026

- Identidad confirmada: cuenta `849533029543`, `us-east-1`, rol `voclabs`. Se recuperó ASG vacío (INC-016), se conservaron PostgreSQL privado y EBS cifrado `vol-0641bf3d4c25b6b34`.
- Terraform agregó gateway EC2 strongSwan y ruta privada GCP; puerto 5432 permanece privado. Se adaptó la renovación de flota a la SCP (INC-018), sin cambiar IAM.
- Escalado real por solicitudes 2→4 en 391,7 s: 2137 respuestas 200, cero errores observados. CPU no logró el ensayo por créditos T3 (INC-019); Unlimited no se activó.
- Fallo de una web: reposición y dos targets saludables en 229,79 s; 183 respuestas 200, cero errores observados. La prueba corresponde al portal estático; las sondas de nuevas VMs requieren reconciliación.
- `prueba_failover.py --ejecutar`: primario aislado, GCP promovido, escritura en GCP y retorno físico a AWS; cinco filas sintéticas preservadas. RTO BD 7,87 s y aplicación 24,66 s en este ensayo.
- HTTPS ALB verificado con `curl --cacert`, sin `-k`: certificado académico autofirmado de 30 días; HTTP sigue habilitado. Certificado y clave privada permanecen fuera de entregables.
- Se ejecutaron apagado, reencendido y reconciliación de peers tras IP efímera vacía (INC-023). El estado final se acredita por el inventario enlazado abajo. La VM de examen ajena al proyecto se conservó.

Comandos: `./nexoandes continuidad`, scripts de pruebas en `integracion/`, `./nexoandes apagar` e `inventario.py`. Evidencias: [estado y límites](../diagramas/excalidraw/ESTADO_2026-11-04.md), [ensayos reales](../integracion/evidencias/20261104/), [inventario final](../infraestructura/evidencias/inventario-final-20261104.json). Las capturas de consola y datos del equipo siguen pendientes; no se modificó el texto de los informes.

Cierre 04/11/2026 14:18 (America/Lima): API confirmó el apagado NexoAndes y la conservación de datos/respaldos. [Comprobación](../integracion/evidencias/20261104/cierre.json). Ciclo final: siete filas coincidentes y restauración de ambas copias con siete filas; [persistencia](../integracion/evidencias/20261104/persistencia-ciclo.json), [restauraciones](../integracion/evidencias/20261104/restauracion-ciclo.json).

## Pausa solicitada — 04/11/2026 14:36 (America/Lima)

Se ejecutó `./nexoandes apagar` y se verificó por API el estado de las tres nubes. NexoAndes no tiene cómputo activo; datos, redes y respaldos conservados. Timer local `nexoandes-respaldos.timer` detenido y deshabilitado por esta pausa; su servicio está inactivo. Las VMs de examen AWS y Antigravity Azure, ajenas al proyecto, permanecen sin cambios. [Evidencia](../integracion/evidencias/20261104/pausa-solicitada.json), [inventario](../infraestructura/evidencias/inventario-pausa-20261104.json). Para reactivar las copias periódicas, consultar `integracion/CONTINUIDAD.md`.

## Consulta de Active Directory — 04/11/2026 20:52 (America/Lima)

Revisión de plantillas Terraform y scripts: NexoAndes no configura Directory Service ni controlador de dominio AD; el core definido sigue siendo AWS (portal y PostgreSQL), con GCP para contingencia y Azure para respaldos. Se intentó confirmar identidad antes de consultar `ds describe-directories`, pero STS respondió `ExpiredToken` (INC-001); Directory Service no se consultó y no se afirma un inventario actual de directorios de toda la cuenta. Sin encender ni modificar recursos. [Evidencia](evidencias/directorio-20261104.json).

## Ubicación Supabase open source — 04/11/2026 21:10 (America/Lima)

Se revisaron requisitos oficiales de Supabase y límites del Learner Lab. Propuesta: EC2 dedicada t3.medium, mínimo 40 GB SSD para la pila, Docker Compose; conservar el PostgreSQL y la réplica actuales. No se afirma disponibilidad de identidad fuera de AWS. Consulta STS antes de operar: `ExpiredToken` (INC-001); no se consultó inventario actual ni se creó, inició o modificó ningún recurso. Presupuesto, cuotas reales y despliegue pendientes. [Propuesta](../integracion/SUPABASE.md), [evidencia](evidencias/supabase-ubicacion-20261104.json).

## Supabase autohospedado — 04/11/2026 21:55 (America/Lima)

STS confirmó cuenta `849533029543`, us-east-1: INC-001 resuelta para esta sesión. Plan revisado sin borrado de datos; `./nexoandes encender --nube aws` creó EC2 privada t3.medium y disco cifrado 40 GB para Supabase, target/API HTTPS y reglas limitadas. Pila fijada v0.8.3, seis servicios saludables. Auth y endpoint privado probados, cuenta sintética .invalid sin correos/SMS. Misma VM y usuario tras stop/start. Web ASG reemplazada y Auth instalado automáticamente en 197,1 s. Pruebas locales: 15 unitarias y 9 mock Terraform correctas. Incidencias INC-026/027/028 corregidas; se conservaron inicializaciones fallidas. Studio privado por túnel SSM temporal. PostgreSQL 15 principal y su EBS permanecen.

Comandos: `integracion/desplegar_supabase.py --ejecutar`, `integracion/supabase/verificar.py`, `integracion/respaldos.py --tipo supabase --generar`; guía reproducible `./nexoandes supabase`. [Estado y evidencia](../integracion/evidencias/20261104/supabase/ESTADO.json), [operación](../integracion/SUPABASE.md), [inventario actual](../infraestructura/evidencias/inventario-supabase-20261104.json). No se modificaron los textos INFORME ni se completaron las capturas de consola pendientes del usuario.


## Nuevo mapa detallado — 04/11/2026

Se creó un segundo [editable Excalidraw](../diagramas/excalidraw/nexoandes-multicloud-detallado.excalidraw), con PNG/SVG, usando el inventario y las pruebas existentes del corte 21:55. Incluye ALB, web en dos zonas, NAT/IGW, PostgreSQL 15 sobre EC2, Supabase privado en app_b, S3/endpoint, CloudWatch/IAM/SSM, réplica IPsec GCP detenida y copias Azure/GCP por el controlador local. Se conservaron el mapa previo y los informes. Generación: `python3 diagramas/excalidraw/herramientas/generar_mapa_detallado.py`; exportación con Excalidraw 0.18 y revisión visual. No se consultaron ni se modificaron servicios cloud en esta edición.


## Revisión del mapa y estado — 04/11/2026 23:01 (America/Lima)

Se confirmó acceso con `./nexoandes comprobar` y se consultaron identidades/recursos de las tres nubes, sin encender, apagar ni cambiar infraestructura. [Inventario de lectura](../infraestructura/evidencias/inventario-mapa-20261104.json): cinco EC2 NexoAndes en ejecución (dos web, PostgreSQL, Supabase y gateway); VM GCP TERMINATED; bucket GCP, Storage y VNet Azure presentes. La VM Azure ajena al proyecto permanece fuera del mapa. No se repitieron pruebas de aplicaciones ni se consultó Cloud Billing API, cuyo bloqueo ya estaba registrado.

El [mapa detallado](../diagramas/excalidraw/nexoandes-multicloud-detallado.excalidraw) incorpora el rol SaaS académico de Supabase, iconos oficiales AWS, detalle de servicios GCP dentro de una sola VM y recursos Azure desglosados. Se retiró la laptop de la topología de servicio; las copias representan flujo lógico bajo demanda, conservando su mecanismo operativo real en la documentación. Exportaciones PNG/SVG regeneradas y revisadas.


## Rediseño Excalidraw con iconos del usuario — 04/11/2026

Se usó el paquete local `Icon-package_07312026.5846e92413caa21490223536cc97f1269e44fa92` indicado por el usuario: 16 SVG copiados sin modificar, con origen y SHA256 registrados en `diagramas/excalidraw/bibliotecas/aws-oficial/FUENTE.json`. El editable detallado se rediseñó con dos zonas, subredes alineadas, ASG común a las web, iconos más visibles y servicios regionales separados. Supabase conserva su rol SaaS académico y la laptop queda fuera. Se regeneraron PNG/SVG y se revisó la apertura. Sin consultas ni cambios cloud en esta edición; se mantiene el corte de inventario 23:01.


## Simplificación visual y controles del mapa — 04/11/2026

Se revisó el mapa detallado: reducción de texto repetido, símbolos para los cinco Security Groups definidos en Terraform, logotipos Supabase/PostgreSQL y controles de privacidad/versionado/retención. Se incorporaron Azure oficial V24, Lucide y Simple Icons con commits, fuentes, licencias y SHA256. El escudo SG es una convención Lucide; no representa AWS Shield ni un servicio nuevo. [Análisis y validación](../diagramas/excalidraw/REVISION_VISUAL.md). Editable, PNG y SVG actualizados; infraestructura e informes sin cambios, conservando el inventario de las 23:01.


## Studio Supabase externo — 04/11/2026 23:33 (America/Lima)

STS confirmó cuenta 849533029543 y región us-east-1; instancia Supabase running sin IP pública y seis contenedores saludables. Usuario autorizó entrada externa con credenciales. Prueba interna previa: sin credenciales 401, incorrectas 401, válidas 200. Plan revisado: solo creación de listener HTTPS 8443, regla de bloqueo /pg y MCP, y actualización SG del ALB; sin reemplazo de VM/disco ni cambios en otras nubes. Terraform fmt/validate y siete escenarios mock correctos. Se aplicó exactamente ese plan, con respaldo privado de estados antes/después.

Prueba externa con CA/nombre TLS verificados: panel sin credenciales 401, clave errónea 401, API Studio sin credenciales 401, panel autenticado 200, rutas meta y MCP 403. Navegador real en /project/default: 200, UI cargada, cero errores JS y APIs de administración 200. Credenciales conservadas en archivo privado modo 600; no expuestas en evidencias. Certificado académico autofirmado; acceso adicional SSM conservado. [Publicación](../integracion/evidencias/20261104/supabase/studio-publicacion.json), [HTTP](../integracion/evidencias/20261104/supabase/studio-externo.json), [navegador](../integracion/evidencias/20261104/supabase/studio-navegador.json), [guía](../integracion/SUPABASE.md).

Validación final de esta publicación: plan AWS posterior con cero cambios; regresión Auth del portal correcta (login 200, acceso sin token 401, HTTP bloqueado 403, logout 204 y token previo 401). [Plan final](../integracion/evidencias/20261104/supabase/studio-plan-final.json). El mapa y exportaciones muestran ahora 443/8443 y Studio autenticado.


## Actualización de documentación por rúbrica — 04/11/2026

Se contrastaron las plantillas y rúbricas con Terraform y evidencias existentes; se actualizaron informes V1/V2, matrices de criterios y guías de capturas. Se conservan los 20 títulos E1, la figura V1 y espacios de fotos. V2 incorpora el mapa actual, plan de seguridad, límites IAM/DR, pruebas Supabase/Studio y modelo económico preliminar. INC-029 registra la corrección de afirmaciones no respaldadas. [Pendientes y responsables](../entregables/ESTADO_RUBRICAS.md). Solo edición/validación local y consulta de fuentes públicas de precios/NIST: sin operaciones cloud ni nuevas fotos; el usuario completará las capturas.

## IAM básico — 05/11/2026 (America/Lima)

Se comprobó identidad 849533029543/us-east-1 y se exportó LabRole (confianza, siete políticas adjuntas, cero inline). Las cinco EC2 NexoAndes tienen LabInstanceProfile e IMDSv2 required. `SSM AWS-RunShellScript` ejecutó STS y HeadBucket desde Supabase: assumed-role/LabRole y S3 correctos. No se alteraron políticas ni confianza Academy. Copias descargadas de S3 y hashes contrastados con Azure/GCP.

Comandos: `./nexoandes comprobar`, `python3 integracion/auditar_iam.py`, consultas CLI/API y `python3 integracion/respaldos.py --tipo postgresql` / `--tipo supabase`. [Alcance, identidades y evidencia](../integracion/IAM.md). Credenciales y planes completos se mantienen privados; no se modificó cómputo ni la configuración del portal.
