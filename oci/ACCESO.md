# Acceso a OCI

## Preparación

Se necesitan cuenta y tenancy, usuario autorizado, región, compartment y clave API registrada en OCI. El 22/10/2026 se instaló OCI CLI 3.95.1 en un entorno Python privado del proyecto, sin modificar Python del sistema. Falta la configuración API de la cuenta ([INC-008](../incidencias/REGISTRO.md)). Instalación reproducible:

```bash
./scripts/instalar-oci-cli.sh
./infraestructura/privado/bin/oci --version
```

Se siguió la [instalación manual oficial en un entorno virtual](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/climanualinst.htm). El controlador encuentra esta CLI local automáticamente.

## Entrar y comprobar

Desde la raíz del proyecto, crea o ubica la configuración local en `oci/privado/`, fuera de los entregables. OCI CLI suele leer `~/.oci/config`; para usar esta carpeta sin copiar el secreto a la documentación:

```bash
chmod 700 oci/privado
OCI_CLI_CONFIG_FILE="$PWD/oci/privado/config" ./infraestructura/privado/bin/oci os ns get
```

El comando de consulta solo funcionará después de configurar el perfil con tenancy, usuario, región, fingerprint y ruta a la clave privada de API. No se ha verificado acceso a una cuenta OCI. No pegues claves ni contenido del archivo `config` en el chat o en Markdown. Puedes partir de [config.example](config.example) y completar los valores únicamente en `oci/privado/config`, con permisos `600`; la clave debe estar registrada en el usuario OCI correspondiente.

Antes de crear recursos, confirma tenancy, región, compartment y límites de la cuenta. Registra cualquier fallo en `../incidencias/REGISTRO.md`.
