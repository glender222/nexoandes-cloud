# IAM básico del proyecto — 05/11/2026

El proyecto utiliza identidades y permisos reales en las tres nubes. AWS y GCP ya los utilizaban; el 05/11 se añadió RBAC de datos en Azure y se cambió la rutina de copias para usar Microsoft Entra ID. No se crearon usuarios ficticios, claves nuevas ni roles administrativos adicionales.

## Identidades y alcance

| Nube | Identidad / mecanismo | Implementado y comprobado |
|---|---|---|
| AWS `849533029543`, `us-east-1` | `LabRole` mediante `LabInstanceProfile`; sesión CLI temporal STS | Las cinco EC2 NexoAndes tienen el perfil y exigen IMDSv2. Exportación de confianza, siete políticas adjuntas y cero inline. STS desde Supabase devuelve `assumed-role/LabRole/i-0ceea48d268d2cb83`; S3 HeadBucket correcto desde el mismo host |
| Azure, suscripción `1db87b28-407f-41d3-b532-41942343157c`, `northcentralus` | Usuario Entra existente; Owner administrativo heredado | Terraform crea `Storage Blob Data Contributor` solo en `nxa1db87b28407f/blobServices/default/containers/postgresql`, no en toda la suscripción. La copia usa `--auth-mode login` y elimina variables de claves/SAS del subproceso |
| GCP `gen-lang-client-0623826791`, `us-central1` | Cuenta de servicio existente `gen-lang-client-0623826791@gen-lang-client-0623826791.iam.gserviceaccount.com` | API testPermissions confirma get/list/create/delete de objetos y lectura del bucket/política. Copias y descarga verifican SHA256. La VM detenida no tiene una cuenta de servicio adjunta: esta identidad corresponde a las herramientas de operación |

La asignación Azure corresponde al usuario con Object ID `3dea043f-f19f-4575-aa57-93db1f8ec20f`. Recurso: `azurerm_role_assignment.backup_operator[0]`; ID de asignación `3857e91a-5847-457f-fe52-4d071ce8495e`. No depende de `encendido`: se conserva el acceso al respaldo con el cómputo apagado. Su Object ID se configura en las variables privadas; no es una contraseña.

## Evidencias y repetición

- [Inventario final: asignación Azure y acceso Entra correctos](evidencias/20261105/iam/inventario-051550Z.json).
- [Inventario inicial con políticas AWS y diagnóstico Azure/GCP](evidencias/20261105/iam/inventario.json).
- [Prueba SSM/STS/S3 desde EC2](evidencias/20261105/iam/aws-prueba-rol.json).
- [Asignación Azure consultada en el ámbito del contenedor](evidencias/20261105/iam/azure-asignacion.json).
- [Plan aplicado Azure: una asignación, sin eliminación](evidencias/20261105/iam/azure-plan.json) y [plan posterior sin cambios](evidencias/20261105/iam/azure-plan-final.json).
- [Copia PG15](evidencias/20261105/respaldos.json) y [copia Supabase](evidencias/20261105/supabase/respaldos.json): lectura S3, upload/download Azure con Entra y upload/download GCP con SA; mismo SHA256 en las tres nubes. No equivalen a una restauración integral nueva.

```bash
./nexoandes comprobar
python3 integracion/auditar_iam.py
python3 integracion/respaldos.py --tipo postgresql
python3 integracion/respaldos.py --tipo supabase
```

`auditar_iam.py` es de lectura, genera un archivo fechado y no modifica roles. La opción `--politica-proyecto` intenta adicionalmente la política global GCP; requiere Cloud Resource Manager API habilitada (INC-031). Las copias son operaciones reales sobre los respaldos existentes, sin generar dumps nuevos salvo que se pida `--generar`. Los archivos de respaldo descargados quedan privados.

## Límites conocidos

- AWS Academy proporciona LabRole/LabInstanceProfile (véase [guía del laboratorio](../aws/README-LEARNER-LAB.md)); conserva una confianza amplia y políticas del laboratorio. Incluye `AmazonSSMManagedInstanceCore`, políticas VocLab y tres políticas EKS/ECR. Se exportaron, sin modificarlas ni eliminar privilegios que puedan necesitar otros ejercicios. INC-002 documenta la restricción histórica de crear roles. No representa mínimo privilegio por servicio.
- En Azure se conservó Owner heredado. El permiso de datos nuevo sí está limitado al contenedor; no elimina la amplitud de la identidad administrativa. La primera prueba inmediata tras crear el rol fue denegada; al propagarse la asignación, las copias con Entra se completaron y coincidieron en SHA256 (INC-030).
- GCP permite operar el bucket; su política conserva roles heredados de proyecto, sin miembros públicos. La API de Cloud Resource Manager estaba deshabilitada al leer la política del proyecto: no se afirma haber enumerado todos los roles globales ni aplicado un recorte de privilegios. No se habilitaron APIs para ampliar la auditoría.
- MFA de consolas no se verificó ni se cambió. Supabase Auth y la credencial administrativa de Studio son identidades de aplicación separadas del IAM cloud.

## Capturas para el entregable

1. AWS IAM → Roles → LabRole → permisos y confianza; EC2 → IAM role de una instancia NexoAndes. Mostrar nombre, perfil y cuenta, sin credenciales de sesión.
2. Azure Storage → contenedor `postgresql` → Access control (IAM) → asignación `Storage Blob Data Contributor` y ámbito. Conservar visible la diferencia con Owner heredado.
3. GCP Cloud Storage → bucket → Permissions; cuenta de servicio usada por las herramientas. No mostrar claves JSON ni afirmar que la VM utiliza esa cuenta.

No es necesario crear usuarios/grupos adicionales para llenar capturas. Las limitaciones del laboratorio y el alcance académico se explican junto a los controles aplicados.

Referencias: [Microsoft: autorización CLI con Entra](https://learn.microsoft.com/en-us/azure/storage/blobs/authorize-data-operations-cli) y [asignación de rol al contenedor](https://learn.microsoft.com/azure/storage/common/storage-auth-aad-rbac-cli).
