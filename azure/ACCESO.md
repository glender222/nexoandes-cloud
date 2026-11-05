# Acceso a Azure

## Estado conocido

`aws/HISTORIAL.md` registra una sesión previa y un fallo de escritura de Azure CLI en `~/.azure/az.sess` ([INC-007](../incidencias/REGISTRO.md)). No se comprobó si esa sesión o suscripción siguen disponibles.

**Verificado el 22/10/2026:** la configuración habitual de Azure CLI (`~/.azure`) sí tiene una sesión Azure for Students activa, suscripción `1db87b28-407f-41d3-b532-41942343157c`, tenant `cfbd88b4-94bc-4fba-98bd-64d0726394a3`. La carpeta local `azure/privado/az-config` no tenía sesión; esto no implicaba que la sesión habitual faltara. El controlador permite seleccionar la ruta existente mediante `azure.cli_config_dir` en su configuración privada, sin copiar tokens.

La política de esta suscripción permite `northcentralus`, `westus3`, `chilecentral`, `brazilsouth` y `westus`; para Terraform se seleccionó `northcentralus`. Verifica la política antes de cambiar de región. `Microsoft.Network` y `Microsoft.Storage` quedaron `Registered` tras su registro explícito; el despliegue real terminó correctamente. Evidencia: `evidencias/terraform-20261022/`.

## Entrar y comprobar

Desde la raíz del proyecto, utiliza un directorio local de configuración escribible:

```bash
mkdir -p azure/privado/az-config
chmod 700 azure/privado/az-config
AZURE_CONFIG_DIR="$PWD/azure/privado/az-config" az login --use-device-code
AZURE_CONFIG_DIR="$PWD/azure/privado/az-config" az account show
AZURE_CONFIG_DIR="$PWD/azure/privado/az-config" az account list --output table
```

Comprueba el identificador de la suscripción y el tenant antes de crear recursos. Si `az login` falla, documenta el error exacto en el registro de incidencias; el método anterior es una guía aún no probada en esta reorganización.

No guardes secretos de una entidad de servicio en `ACCESO.md`. Si se habilita acceso no interactivo, registra aquí únicamente el nombre de las variables y el procedimiento autorizado para obtenerlas.
