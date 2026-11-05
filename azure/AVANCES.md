# Avances de Azure

**Última verificación real:** 2026-10-22. Suscripción Azure for Students comprobada y seis recursos Terraform desplegados en `northcentralus`; resultados y estado final en [evidencias](evidencias/terraform-20261022/README.md).

| Elemento | Estado | Siguiente paso |
|---|---|---|
| Cuenta, tenant y suscripción | Datos de una sesión anterior en `aws/HISTORIAL.md` | Confirmar identidad y permisos actuales |
| Azure CLI | Sesión habitual `~/.azure` válida; directorio local vacío (INC-012) | Renovar sesión cuando caduque |
| Red y recursos | VNet, GatewaySubnet y Blob privado/versionado administrados con Terraform | VPN y monitoreo opcionales sin activar |
| Integración multicloud | Dump copiado de S3 a Blob y descargado con SHA256 idéntico | Automatizar copias; VPN y OCI pendientes |

Cuando se ejecute trabajo nuevo, añade fecha, recurso, comando o procedimiento, resultado y enlace a evidencia. Registra incidencias nuevas solo en `../incidencias/REGISTRO.md`.

## Preparación Terraform — 22/10/2026

- Decisión del usuario: administrar AWS, Azure y OCI con Terraform y un control común de encendido/apagado que conserva datos.
- Se creó `azure/terraform/`: Resource Group, VNet, Blob privado/versionado y opciones de VPN Gateway y Log Analytics. Ambos servicios opcionales están deshabilitados inicialmente. Terraform 1.17.0 / AzureRM 5.10.0 fijados con lockfile.
- `terraform validate` correcto y dos pruebas `terraform test` con proveedor simulado: crear el gateway al encender, retirarlo al apagar y conservar almacenamiento. No hubo despliegue real de Azure.
- Consulta real `AZURE_CONFIG_DIR="$PWD/azure/privado/az-config" az account show --query '{subscription:id,tenant:tenantId,name:name}' --output json`: `Please run 'az login' to setup account.` Falta iniciar sesión y confirmar tenant/suscripción (INC-012).
- Azure queda deshabilitada en la configuración privada del control; no se inventaron identificadores. Guía: [Control multicloud](../infraestructura/README.md).

## Continuidad y despliegue real — 22/10/2026

- La preparación anterior usaba una carpeta CLI vacía. Se consultó la configuración habitual `~/.azure` y se verificaron suscripción `1db87b28-407f-41d3-b532-41942343157c` y tenant `cfbd88b4-94bc-4fba-98bd-64d0726394a3`. Se configuró `cli_config_dir` sin copiar tokens y se habilitó Azure en el controlador (INC-012).
- `az policy assignment list` confirmó regiones permitidas; se seleccionó `northcentralus`. `az provider register` para Network y Storage terminó con ambos `Registered` (INC-014). No se intentó desplegar en `eastus`.
- `./nexoandes plan encender --nube azure`: 6 altas, 0 cambios y 0 bajas. `./nexoandes encender --nube azure` terminó correctamente: RG `nexoandes-lab`, VNet `nexoandes-vnet`, `GatewaySubnet`, Storage Account `nxa1db87b28407f`, contenedor privado `postgresql` y política de retención. VPN Gateway y Log Analytics siguen deshabilitados. Log completo sensible en `infraestructura/privado/despliegue-azure.log`.
- Se descargó el dump real `postgresql/20261022T205410Z.dump` desde S3, se subió a Blob y se descargó nuevamente. Los 1868 bytes coincidieron por SHA256. No se documentaron claves de almacenamiento; se usaron solo en el entorno del proceso y se eliminaron los archivos temporales. Esta fue una copia manual, no una integración automática ni una restauración en Azure. [Resultado](evidencias/terraform-20261022/copia-respaldo-verificada.json).
- `./nexoandes apagar` terminó correctamente en Azure y AWS. Se conservaron los recursos persistentes de Azure; `encendido=false` quedó guardado. Después del apagado se descargó nuevamente el dump Blob y coincidió con el SHA256 original: [prueba](evidencias/terraform-20261022/respaldo-apagado-final.json). No había VPN Gateway ni cómputo Azure habilitado para detener. El almacenamiento conservado puede seguir consumiendo crédito.
- `./nexoandes plan apagar` repetido: cero cambios en ambas nubes; evidencia `plan-apagar-sin-cambios.json`.

## Despliegue de Red, Respaldo Tri-Cloud y Apagado Efímero — 29/10/2026

- Se aprovisionaron mediante Terraform los recursos de enlace de red para la arquitectura híbrida: Local Network Gateway `nexoandes-lng-aws` (apuntando a la IP de AWS `44.201.53.31` con espacio `10.10.0.0/16`) y la IP pública estándar `nexoandes-vpn-ip` (`172.183.128.185`).
- Verificación de replicación tri-cloud del dump PostgreSQL `20261029T162807Z.dump` (1,868 bytes) en el contenedor `postgresql` del Storage Account `nxa1db87b28407f`. Hash criptográfico SHA-256 idéntico a AWS y GCP (`39941843837fc2570e8becafaf244ef3e019a150b956c62c79537edc886423bb`).
- Se ejecutó `./nexoandes apagar --nube azure`, destruyendo de forma segura los recursos con costo horario (`azurerm_public_ip` y `azurerm_local_network_gateway`).
- Auditoría vía `az resource list -g nexoandes-lab`: confirmada la eliminación de la IP pública y la conservación del Storage Account con los respaldos y la VNet, garantizando $0.00 en consumo horario no planificado.

## Despliegue de VM para Antigravity con Docker — 01/11/2026

- Se identificó y resolvió restricción de capacidad para tamaños clásicos v1 en `northcentralus` utilizando la nueva generación `Standard_B2als_v2` (AMD x86_64, 2 vCPUs, 4 GB RAM).
- Se creó el grupo de recursos `agy-docker-rg` en `northcentralus` y se aprovisionó la máquina virtual `agy-docker-vm` con Ubuntu 24.04 LTS y disco OS de 30 GB.
- Vía cloud-init se habilitó un archivo de Swap de 2 GB y se instaló Docker CE (`v29.9.2`) y Docker Compose (`v5.6.1`), agregando al usuario `azureuser` al grupo `docker`.
- Verificación completada exitosamente: IP pública asignada `20.25.246.153`, conectividad SSH operativa y Docker listo para ejecutar contenedores 24/7.

## Comprobación de acceso — 04/11/2026

- Consulta realizada el 04/11/2026 10:33 (America/Lima) usando la sesión CLI existente en `~/.azure`, sin cambiar la suscripción por defecto ni iniciar un login nuevo.
- `az account show` y GET remoto de la suscripción `1db87b28-407f-41d3-b532-41942343157c` respondieron correctamente: Azure for Students, estado `Enabled`; tenant coincidente con el proyecto.
- La sesión permite la consulta de administración comprobada; no requiere renovación para estas lecturas. No se verificaron saldo, créditos ni permisos de escritura.
- Sin cambios en recursos ni credenciales. [Resultado de las consultas](../infraestructura/evidencias/acceso-20261104.json).

## Continuidad V2 y pruebas — 04/11/2026

- Suscripción `1db87b28-407f-41d3-b532-41942343157c`, región `northcentralus`, sesión habitual comprobada.
- Se conservaron Blob privado/versionado y VNet. `respaldos.py --generar` copió dumps desde S3 por HTTPS y descargó las copias para comparar SHA256 entre las tres nubes.
- Se restauró un dump descargado de Azure en una BD temporal GCP y se verificó por SQL; prueba original en `failover.json`. Igualdad de hashes y restauración son comprobaciones separadas.
- VPN Gateway y monitoreo ampliado permanecen deshabilitados por costo; Blob no requiere VPN para estas APIs. Se retiró una PSK predeterminada de la plantilla opcional; no se crearon recursos de esa VPN.
- El costo consultado de noviembre corresponde a toda la suscripción, no a saldo disponible ni exclusivamente a NexoAndes. La VM Antigravity ajena al proyecto se conservó encendida.

Comandos: `./nexoandes continuidad`, scripts de pruebas en `integracion/`, `./nexoandes apagar` e `inventario.py`. Evidencias: [estado y límites](../diagramas/excalidraw/ESTADO_2026-11-04.md), [ensayos reales](../integracion/evidencias/20261104/), [inventario final](../infraestructura/evidencias/inventario-final-20261104.json). Las capturas de consola y datos del equipo siguen pendientes; no se modificó el texto de los informes.

Cierre 04/11/2026 14:18 (America/Lima): API confirmó el apagado NexoAndes y la conservación de datos/respaldos. [Comprobación](../integracion/evidencias/20261104/cierre.json). Ciclo final: siete filas coincidentes y restauración de ambas copias con siete filas; [persistencia](../integracion/evidencias/20261104/persistencia-ciclo.json), [restauraciones](../integracion/evidencias/20261104/restauracion-ciclo.json).

## Pausa solicitada — 04/11/2026 14:36 (America/Lima)

Se ejecutó `./nexoandes apagar` y se verificó por API el estado de las tres nubes. NexoAndes no tiene cómputo activo; datos, redes y respaldos conservados. Timer local `nexoandes-respaldos.timer` detenido y deshabilitado por esta pausa; su servicio está inactivo. Las VMs de examen AWS y Antigravity Azure, ajenas al proyecto, permanecen sin cambios. [Evidencia](../integracion/evidencias/20261104/pausa-solicitada.json), [inventario](../infraestructura/evidencias/inventario-pausa-20261104.json). Para reactivar las copias periódicas, consultar `integracion/CONTINUIDAD.md`.

## Supabase autohospedado — 04/11/2026 21:55 (America/Lima)

Se recibió por HTTPS una copia del respaldo Supabase generado en AWS; descarga y SHA256 coincidentes entre los tres proveedores. No se arrancó ni creó cómputo de NexoAndes en esta nube. La restauración selectiva de usuarios se probó en una BD temporal AWS, no se afirma restauración integral o failover Supabase en azure.

Comandos: `integracion/desplegar_supabase.py --ejecutar`, `integracion/supabase/verificar.py`, `integracion/respaldos.py --tipo supabase --generar`; guía reproducible `./nexoandes supabase`. [Estado y evidencia](../integracion/evidencias/20261104/supabase/ESTADO.json), [operación](../integracion/SUPABASE.md), [inventario actual](../infraestructura/evidencias/inventario-supabase-20261104.json). No se modificaron los textos INFORME ni se completaron las capturas de consola pendientes del usuario.


## Revisión del mapa y estado — 04/11/2026 23:01 (America/Lima)

Se confirmó acceso con `./nexoandes comprobar` y se consultaron identidades/recursos de las tres nubes, sin encender, apagar ni cambiar infraestructura. [Inventario de lectura](../infraestructura/evidencias/inventario-mapa-20261104.json): cinco EC2 NexoAndes en ejecución (dos web, PostgreSQL, Supabase y gateway); VM GCP TERMINATED; bucket GCP, Storage y VNet Azure presentes. La VM Azure ajena al proyecto permanece fuera del mapa. No se repitieron pruebas de aplicaciones ni se consultó Cloud Billing API, cuyo bloqueo ya estaba registrado.

El [mapa detallado](../diagramas/excalidraw/nexoandes-multicloud-detallado.excalidraw) incorpora el rol SaaS académico de Supabase, iconos oficiales AWS, detalle de servicios GCP dentro de una sola VM y recursos Azure desglosados. Se retiró la laptop de la topología de servicio; las copias representan flujo lógico bajo demanda, conservando su mecanismo operativo real en la documentación. Exportaciones PNG/SVG regeneradas y revisadas.


## Estructura visual de Azure — 04/11/2026

Se reorganizó el [Excalidraw detallado](../diagramas/excalidraw/nexoandes-multicloud-detallado.excalidraw) según `azure/terraform/main.tf`: grupo nexoandes-lab, Storage Account LRS, contenedor postgresql privado y políticas; VNet/GatewaySubnet como recurso separado dentro del grupo. Se ubicó el candado en el contenedor y se usaron SVG oficiales Resource Groups, Storage Accounts, Blob Block y Virtual Networks. Grupos editables anidados, PNG/SVG regenerados e inspeccionados e importación Excalidraw correcta. Sin consultas ni cambios cloud; se conserva el corte de inventario 23:01.

## IAM básico — 05/11/2026 (America/Lima)

Se comprobó suscripción 1db87b28-407f-41d3-b532-41942343157c/tenant y región northcentralus. Plan Terraform revisado: solo azurerm_role_assignment.backup_operator[0] create. Apply: 1 añadido, 0 cambiados, 0 destruidos; plan posterior sin cambios. Storage Blob Data Contributor al usuario existente, ámbito único contenedor postgresql. `integracion/respaldos.py` usa --auth-mode login, sin listKeys ni claves/SAS heredadas. Primera denegación por propagación, posterior upload/download y SHA256 coincidentes. INC-030 resuelta.

Comandos: `./nexoandes comprobar`, `python3 integracion/auditar_iam.py`, consultas CLI/API y `python3 integracion/respaldos.py --tipo postgresql` / `--tipo supabase`. [Alcance, identidades y evidencia](../integracion/IAM.md). Credenciales y planes completos se mantienen privados; no se modificó cómputo ni la configuración del portal.
