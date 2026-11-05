# Acceso a Google Cloud Platform (GCP)

> **Acceso actualizado el 04/11/2026:** el usuario autorizó la comprobación e implementación con la cuenta de servicio existente. Compute y Storage respondieron correctamente. No hace falta crear proyectos ni reemplazar la clave para este flujo. Usar `./nexoandes comprobar --nube gcp`; las opciones siguientes describen la preparación inicial, no una tarea pendiente actual.

## Requisitos Previstos

1. Cuenta de Google Cloud (personal o institucional UPeU) con proyecto activo y facturación / créditos habilitados.
2. Google Cloud CLI (`gcloud`) instalada localmente o en el entorno del agente.
3. Proyecto identificado por su `PROJECT_ID` (e.g. `nexoandes-multicloud`).

## Procedimiento Futuro de Configuración

Cuando el usuario indique configurar el acceso:

### Opción A: Autenticación Interactiva (Desarrollo local)
```bash
gcloud auth login
gcloud config set project <PROJECT_ID>
gcloud auth application-default login
```

### Opción B: Cuenta de Servicio (Service Account para Terraform)
1. Crear una cuenta de servicio con roles mínimos:
   - `roles/storage.admin` (para buckets de respaldo)
   - `roles/compute.instanceAdmin.v1` (para cómputo en contingencia)
   - `roles/compute.networkAdmin` (para red VPC)
2. Descargar la clave privada en formato JSON y guardarla localmente en:
   `gcp/privado/sa-key.json` (con permisos `600`).
3. El archivo `gcp/privado/` está excluido de Git y nunca debe exponerse en documentación o entregables.

## Comprobación Futura
```bash
gcloud config get-value project
gcloud storage buckets list
```
