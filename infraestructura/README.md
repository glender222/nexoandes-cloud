# Control multicloud con Terraform

Decisión del usuario, 22/10/2026: continuar en AWS `849533029543` y administrar la infraestructura multicloud con Terraform. El 28/10/2026 se resolvió reemplazar OCI por Google Cloud (GCP); el acceso GCP y la continuidad V2 se verificaron el 04/11/2026; ver `integracion/CONTINUIDAD.md`. Los recursos históricos de `669186512136` no se importan ni se confunden con el despliegue nuevo.

**Comprobado el 22/10/2026:** AWS y Azure están habilitadas y tienen despliegues reales administrados por este control. AWS superó encendido, apagado y reencendido conservando la misma DB y sus datos; el portal respondió HTTP 200. Azure creó seis recursos Terraform en `northcentralus`. Ese párrafo corresponde al estado histórico del 22/10. La implementación y las pruebas posteriores de GCP están en `integracion/CONTINUIDAD.md` y `gcp/AVANCES.md`. OCI se conserva archivado como referencia en `oci/`.

**Estado al terminar:** apagado conjunto completado, con datos conservados en ambas nubes. Un nuevo `plan apagar` consultó los recursos reales y dio cero cambios en AWS y Azure. Se probó el botón GTK «Ver estado guardado»: ejecutó el controlador, bloqueó los botones mientras trabajaba y los habilitó al terminar. [Evidencia del panel](evidencias/panel-estado-20261022.json).

**Supabase autohospedado:** `./nexoandes supabase` prepara la sesión AWS; `apagar` detiene también esa misma VM y conserva su EBS cifrado de 40 GB. Guía y límites: [SUPABASE.md](../integracion/SUPABASE.md).

## Acciones disponibles

```bash
./nexoandes panel                   # Ventana con botones
./nexoandes comprobar               # Identidades de las nubes habilitadas
./nexoandes plan encender           # Revisar sin crear recursos
./nexoandes encender                # Planificar y aplicar en las nubes habilitadas
./nexoandes plan apagar
./nexoandes apagar                  # Conservar datos y retirar cómputo temporal
./nexoandes estado                  # Último estado Terraform guardado, no prueba en vivo
./nexoandes respaldar-estado
```

También existe el lanzador **NexoAndes — Control multicloud** en el menú de aplicaciones de GNOME, instalado con `./scripts/instalar-panel.sh`. Usa `--nube aws`, `--nube azure` o `--nube gcp` para operar solo una nube. Por defecto, `todas` recorre las habilitadas y muestra explícitamente cuáles siguen pendientes.

Las acciones Encender y Apagar del panel planifican y aplican el cambio. Para inspeccionar primero el resultado, usa Ver plan. La primera ejecución crea recursos y genera consumo en la cuenta correspondiente. No hay un botón para borrar todos los datos.

## Qué significa apagar

Se adopta como comportamiento conservador conservar bases de datos y respaldos. No equivale a `terraform destroy`, ni garantiza gasto cero.

| Nube | Se detiene o retira | Se conserva |
|---|---|---|
| AWS | EC2 PostgreSQL queda `stopped`; se eliminan ASG e instancias web, Launch Template, ALB/listeners/Target Group, NAT, su EIP, ruta privada a Internet y alarmas temporales | VPC/subredes/SG/rutas locales, endpoint Gateway S3, EC2 DB detenida, disco de datos EBS cifrado, disco de arranque DB y bucket S3 |
| Azure | Si se habilitó, se elimina VPN Gateway y su IP pública | Resource Group, VNet, GatewaySubnet, Storage Account, contenedor de respaldos; Log Analytics si se habilitó |
| GCP | Instancia Compute Engine pasa a `TERMINATED`/detenida | Discos persistentes de arranque/datos, VPC/subredes, Cloud Storage de respaldos |

El almacenamiento AWS y Azure puede seguir cobrando al apagar. Log Analytics puede tener consumo adicional si se habilita.

El NAT y el ALB no son máquinas que podamos dejar detenidas: el ciclo de laboratorio los elimina y recrea. Por eso la URL del ALB y la IP del NAT pueden cambiar al encender. El gateway Azure puede tardar considerablemente en recrearse. El flujo `./nexoandes continuidad` reconcilia IPs y configura IPsec AWS↔GCP; la VPN Azure sigue opcional y deshabilitada.

## Estructura y estado

- `aws/terraform/`: VPC, cinco subredes, red, PostgreSQL 15 con disco persistente, respaldos horarios a S3, dos EC2 web con ALB, ASG 2–4, escalado por CPU y alarmas.
- `azure/terraform/`: VNet, almacenamiento de respaldos privado con versionado, gateway VPN y Log Analytics opcionales. No copia datos desde AWS por sí mismo.
- `gcp/terraform/`: VPC, Cloud Storage para réplica de respaldos, Compute Engine y disco persistente para réplica y contingencia (probados el 04/11/2026).
- `oci/terraform/`: Código archivado con fines históricos.
- `infraestructura/control.py`: prevalidación de identidades, planes, protección de datos, ejecución por nube y registro de resultados.
- `infraestructura/privado/config.json`: selección de cuentas, regiones, nubes habilitadas y variables.
- `infraestructura/privado/estado/<nube>/<identidad>-<region>.tfstate`: estados independientes por nube, cuenta y región.
- `infraestructura/privado/operaciones/`: planes binarios, parámetros y resultado de cada operación.
- `infraestructura/privado/respaldos/`: copias locales de estados y configuración antes de aplicar, después de cada nube aplicada y ante fallos.

La separación evita que el fin de una sesión AWS borre el estado de Terraform. El directorio privado completo y los planes se tratan como sensibles: los proveedores pueden incluir claves o atributos confidenciales en el estado. No se versionan. Los archivos `.terraform.lock.hcl` sí se conservan para fijar los proveedores.

La copia automática está en el mismo equipo; no cubre pérdida del portátil/disco. Guarda adicionalmente una copia cifrada del respaldo de estados en otro lugar. Un estado Terraform no contiene los registros de PostgreSQL: también se necesitan respaldos de la base de datos.

## Preparación inicial

```bash
./scripts/instalar-terraform.sh
./nexoandes configurar
nano infraestructura/privado/config.json
./scripts/instalar-panel.sh
./nexoandes comprobar
./nexoandes plan encender
```

El instalador usa Terraform **1.17.0**, descarga oficial HTTPS y verificación SHA256. Proveedores fijados: AWS **6.70.0**, AzureRM **5.10.0** y OCI **9.11.0**. La selección se verificó con el registro oficial el 22/10/2026.

### AWS Academy

La configuración actual habilita AWS `849533029543` / `us-east-1` y Azure; el archivo de ejemplo empieza únicamente con AWS habilitada. No usa el perfil `academy` vencido: lee `aws/privado/academy-session.env`, sin ejecutar su contenido. Admite las tres líneas `export`, variables sin export o el bloque INI `[default]`.

Antes de encender, inicia el Learner Lab y renueva las tres credenciales si caducaron. `comprobar` valida la cuenta y la región de trabajo; el proveedor restringe `allowed_account_ids`. Terraform no inicia Vocareum, no amplía el presupuesto ni renueva automáticamente las credenciales académicas.

Al terminar una sesión los recursos se conservan según las reglas del lab. En una sesión nueva, el laboratorio puede arrancar también la EC2 DB que dejaste detenida: vuelve a ejecutar `./nexoandes apagar` si no vas a trabajar. El apagado necesita credenciales vigentes; conviene hacerlo antes de que termine el temporizador.

El flujo V2 y sus pruebas se describen en [CONTINUIDAD.md](../integracion/CONTINUIDAD.md).

El módulo reutiliza `LabInstanceProfile`, sin crear roles ni usuarios IAM. No abre SSH. IMDSv2 y discos cifrados están configurados. PostgreSQL permite acceso por SG desde la capa web, pero no crea una contraseña de aplicación ni implementa pedidos; el portal sigue siendo informativo. HTTPS requiere un certificado ACM de esta cuenta/región mediante `certificate_arn`; con el valor vacío, el portal de laboratorio sirve HTTP y no se presenta como HTTPS configurado.

**Compatibilidad S3 con Academy (INC-013):** el proveedor AWS consulta `GetBucketObjectLockConfiguration` al refrescar `aws_s3_bucket`, operación denegada por la SCP del laboratorio incluso sin activar Object Lock. El alta del contenedor usa por ello un recurso integrado `terraform_data` con un provisioner local acotado (`aws/terraform/bootstrap-bucket.py`). Comprueba cuenta, propietario, región y etiqueta del proyecto, y crea el bucket solo si no existe. No incorpora ninguna operación de borrado. El bloqueo público, cifrado, propiedad, versionado y retención se administran con recursos nativos AWS del proveedor. No se modifican permisos ni se usa Object Lock.

Antes de cada plan el controlador consulta `HeadBucket`: si detecta que un bucket ya administrado desapareció y la acción es Encender, cambia una generación local para que Terraform vuelva a crear el contenedor. Ese nuevo bucket estará vacío hasta restaurar sus datos. Apagar nunca crea un bucket. Esta excepción es específica del Learner Lab; fuera de este entorno conviene usar el recurso nativo cuando los permisos permitan su lectura. El marcador `terraform_data` puede reemplazarse sin borrar S3 y es la única excepción adicional del controlador a la protección de reemplazos persistentes.

El disco de datos de 20 GB es independiente y se monta antes de inicializar PostgreSQL. El arranque no formatea un volumen que ya tenga sistema de archivos. Los datos y la EC2 DB tienen `prevent_destroy`; cambios que requieran reemplazarlos se detienen para revisión. El respaldo horario está programado mientras la DB está encendida, con `pg_dump` y S3. El 22/10/2026 se ejecutó manualmente el respaldo y se restauró el dump en una base temporal, comprobando el marcador de prueba. Las notificaciones de alarmas aún requieren prueba real. Se recomienda añadir registros de acceso S3, eventos de datos CloudTrail y métricas CloudWatch, revisando primero permisos y costo del laboratorio.

### Azure

El controlador admite `cli_config_dir` en la configuración privada para reutilizar una sesión Azure CLI existente. Si está vacío usa `azure/privado/az-config`; no se copian tokens entre carpetas. El 22/10/2026 se encontró una sesión Azure for Students en `~/.azure` y una política de regiones que permite `northcentralus` (seleccionada), `westus3`, `chilecentral`, `brazilsouth` y `westus`. El ejemplo `eastus` debe ajustarse a la política real de cada cuenta.

1. Sigue `azure/ACCESO.md` para iniciar sesión con `AZURE_CONFIG_DIR` local.
2. Confirma la suscripción y tenant; pon sus identificadores en la configuración privada.
3. Selecciona un nombre global único de Storage Account y una región admitida por tu suscripción.
4. Comprueba que `Microsoft.Network` y `Microsoft.Storage` estén registrados. Si habilitas Log Analytics, registra también `Microsoft.OperationalInsights`.
5. Cambia `habilitada` a `true` y ejecuta `./nexoandes comprobar --nube azure`, seguido de `plan encender`.

VPN y Log Analytics empiezan deshabilitados para no dar por aprobados costos aún desconocidos. El almacenamiento usa Hot para evitar introducir la permanencia mínima de Cool en pruebas breves; se puede revisar después. El contenedor no es público; la configuración inicial usa el endpoint HTTPS público autenticado. Las restricciones adicionales de red y las identidades para copias entre nubes están pendientes.

### OCI

1. Sigue `oci/ACCESO.md`: la CLI local ya está instalada (`./scripts/instalar-oci-cli.sh` permite repetir la instalación). Configura `oci/privado/config` y registra una clave API en tu cuenta.
2. Confirma tenancy, región home, compartment, disponibilidad de A1 y consumo Always Free ya existente.
3. Completa `tenancy`, `region`, `compartment_ocid`, `availability_domain` e `image_ocid` (imagen oficial Ubuntu 22.04/24.04 ARM64).
4. Si necesitas Bastion, configura `bastion_client_cidrs` con tus redes autorizadas; sin esa lista no se crea Bastion ni se abre el acceso SSH.
5. Habilita la nube y ejecuta comprobar y plan. El proveedor comprueba que la región coincida con la home antes de crear la VCN.

El host no tiene puertos públicos abiertos por defecto. IPsec solo admite UDP 500/4500 desde los extremos AWS que se configuren explícitamente. Se usa NAT-T; ninguna PSK aparece en el código. El bucket versionado rota objetos y versiones anteriores del prefijo `postgresql/` a los siete días. La retención no limita automáticamente los GB: vigila el total de Object Storage, incluidas otras copias y versiones. La réplica exige PostgreSQL de la misma versión mayor que AWS; no se afirma que esté instalada, sincronizada o promovida.

## Fallos y recuperación

Antes de encender se comprueban todas las nubes habilitadas y se preparan todos sus planes. Al apagar, si una sesión ha caducado o una nube falla, el controlador intenta apagar las demás y termina con error y un registro de apagado parcial; no presenta el resultado como un apagado completo. El controlador bloquea la eliminación o reemplazo de recursos persistentes y rechaza cualquier creación durante Apagar. Si no existe estado administrado, Apagar no inicializa una nube nueva.

No hay una transacción atómica entre proveedores. Si una nube falla después de que otra haya aplicado, se conserva el estado real alcanzado; `operaciones/.../estado.json` indica cuáles terminaron. Corrige acceso/permisos y vuelve a planificar. No se elimina infraestructura automáticamente para intentar revertir un fallo.

Si se borran/resetéan los recursos desde fuera, Terraform puede reconstruir la infraestructura a partir del código, pero recuperar datos exige respaldos accesibles. Si se pierde el estado local, restaura su copia antes de aplicar; no ejecutes a ciegas sobre recursos existentes porque podrías duplicarlos. El panel no hace `terraform destroy`, `state rm` ni importaciones automáticas.

## Verificación reproducible

```bash
./nexoandes validar
python3 -m unittest discover -s infraestructura/tests -v
```

Los tests `tests/ciclo.tftest.hcl` usan proveedores simulados. Azure y OCI aplican un encendido simulado y planifican el apagado sobre ese estado para comprobar que se conservan los recursos de datos. AWS compara planes de encendido y apagado, sin ejecutar su provisioner S3: comprueba cómputo temporal, DB detenida y configuración persistente. Se ejecutan con `terraform test` y un `TF_DATA_DIR` de validación, sin desplegar en las cuentas reales. No sustituyen las pruebas reales del portal, de respaldo/restauración ni del ciclo completo. `./scripts/verificar-terraform.sh` reúne las verificaciones locales.

## Referencias técnicas

- [Estado de encendido EC2](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ec2_instance_state).
- [Costo y eliminación del NAT](https://aws.amazon.com/vpc/pricing/).
- [Backend local y bloqueo de estado Terraform](https://developer.hashicorp.com/terraform/language/state/backends).
- [Datos sensibles en planes y estados](https://developer.hashicorp.com/terraform/language/manage-sensitive-data).
- [Recurso integrado terraform_data](https://developer.hashicorp.com/terraform/language/resources/terraform-data) y [provisioners](https://developer.hashicorp.com/terraform/language/resources/provisioners/local-exec).
- [Proveedor AzureRM y autenticación CLI](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs).
- [Estado RUNNING/STOPPED de OCI Compute](https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_instance).
- [Límites Always Free de OCI](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm).
