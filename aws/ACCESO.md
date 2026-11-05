# Acceso a AWS Academy

Referencia del laboratorio: [README de Learner Lab](README-LEARNER-LAB.md), proporcionado por el usuario y con actualización original del 24/06/2025. Incluye Start Lab, AWS Details, consola, CloudShell, SSH y restricciones del entorno.

## Requisitos

Acceso al laboratorio Vocareum y AWS CLI. El historial usa la región `us-east-1` y el perfil `academy`. Las credenciales del laboratorio caducan; una sesión histórica no garantiza acceso hoy.

Para el flujo nuevo con Terraform, utiliza `./nexoandes comprobar --nube aws` desde la raíz y consulta [Control multicloud](../infraestructura/README.md). Lee las credenciales privadas vigentes sin depender del perfil `academy` anterior. Encender/apagar no renueva la sesión del Learner Lab.

**Comprobación del 22/10/2026:** el lector `academy-aws` autentica en la cuenta `849533029543`, diferente de la cuenta histórica `669186512136`. El perfil local `academy` devolvió `ExpiredToken`; no debe confundirse con las credenciales vigentes del archivo privado. Revisa el [diagnóstico de cambio de cuenta](evidencias/acceso-20261022T201923Z-849533029543/RESUMEN.md) antes de operar.

## Entrar y comprobar

1. Inicia el laboratorio en Vocareum y obtén las credenciales temporales desde **AWS Details**. No las pegues en archivos Markdown ni en `start-lab.sh`.
2. Configúralas en tu perfil local `academy` o expórtalas en la terminal que usará el agente.
3. Comprueba la identidad antes de cualquier operación:

```bash
AWS_PROFILE=academy AWS_DEFAULT_REGION=us-east-1 aws sts get-caller-identity
```

Si usas variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` y `AWS_SESSION_TOKEN` en lugar del perfil, comprueba con `aws sts get-caller-identity`. Si recibes `ExpiredToken` o `InvalidClientTokenId`, renueva las credenciales en Vocareum. No supongas que la infraestructura falló.

Si las tres líneas `export` de CloudShell se guardaron localmente en `privado/academy-session.env`, puedes ejecutar consultas sin modificar el perfil vencido:

```bash
aws/infraestructura/academy-aws sts get-caller-identity
```

El archivo privado tiene permisos `600` y no debe enviarse al chat ni incluirse en los entregables.

Para repetir todas las consultas de infraestructura sin reescribir comandos:

```bash
aws/infraestructura/inventario-lectura.sh
```

Solo usa operaciones `get`, `describe` y `list` en AWS; guarda los resultados JSON en `aws/evidencias/inventario-actual/`.

## Verificar recursos registrados

Desde la raíz del proyecto:

```bash
AWS_PROFILE=academy AWS_DEFAULT_REGION=us-east-1 aws ec2 describe-vpcs --filters Name=tag:Name,Values=AWsAcademy-VPC
AWS_PROFILE=academy AWS_DEFAULT_REGION=us-east-1 aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names AWsAcademy-ASG
AWS_PROFILE=academy AWS_DEFAULT_REGION=us-east-1 aws elbv2 describe-load-balancers --names AWsAcademy-ALB
```

`infraestructura/infra-params.env` contiene IDs de la sesión anterior; verifica cada uno antes de reutilizarlo.

## EC2 por SSH

La clave existente está en `privado/AWsAcademy-Key.pem` y conserva permiso `400`. La IP privada de una instancia no es accesible directamente desde Internet: primero debe existir una ruta autorizada, por ejemplo una VPN o bastión. Los IDs y direcciones de `HISTORIAL.md` pueden haber cambiado. Consulta [INC-006](../incidencias/REGISTRO.md) sobre la exposición de SSH y la clave.

## Reinicio del laboratorio

`infraestructura/start-lab.sh` usa las credenciales ya configuradas en el entorno o perfil. Con el perfil `academy`, se invocaría desde la raíz con `AWS_PROFILE=academy aws/infraestructura/start-lab.sh`. Revísalo antes de ejecutarlo: modifica el ASG, puede crear un listener y registra instancias en el Target Group. El script no renueva credenciales ni sustituye la comprobación del estado actual.
