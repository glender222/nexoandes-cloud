# Guía para agentes

## Alcance

Este proyecto final usa AWS Academy, Azure y Google Cloud (GCP) — OCI fue reemplazado por Google Cloud el 28/10/2026; el acceso a GCP se verificó el 04/11/2026 y la continuidad V2 se documenta en `integracion/CONTINUIDAD.md`. Continúa desde el estado real; no des por desplegado algo que aparezca solo en `aws/HISTORIAL.md` o en una plantilla. No uses Graphify para este proyecto.

## Fuente del Entregable 1

`entregables/entregable-01/INFORME.md` es el texto fuente que el usuario convertirá a Word o al formato presentable de la entrega. Conserva los 20 títulos, nombres y orden de `referencias/ENTREGABLE1.md`; coloca en el informe únicamente contenido destinado al documento final. Guarda estado, tareas pendientes e instrucciones para agentes en `entregables/entregable-01/README.md` y `REVISION_RUBRICA.md`, fuera del informe. No elimines los espacios reservados para las capturas que tomará el usuario ni presentes pruebas pendientes como realizadas.

## Orden de lectura

1. [README.md](README.md): mapa general y estado resumido.
2. `aws/README.md`, `azure/README.md`, `gcp/README.md` (y el histórico `oci/README.md`): responsabilidad y estado de cada nube.
3. `ACCESO.md` de la nube necesaria: cómo configurar y comprobar la sesión.
4. [incidencias/REGISTRO.md](incidencias/REGISTRO.md): fallos conocidos y soluciones intentadas.
5. [integracion/README.md](integracion/README.md), [guía del Entregable 1](entregables/entregable-01/README.md) y [texto del informe](entregables/entregable-01/INFORME.md).

## Antes de operar en la nube

- Confirma cuenta, suscripción o proyecto y región. Las credenciales de AWS Academy son temporales.
- Consulta incidencias antes de repetir comandos que ya fallaron.
- Para cambios con costo, publicación o efectos externos, prepara y revisa el resultado conforme a la autorización del usuario.
- Registra lo que ejecutaste en el `AVANCES.md` correspondiente: fecha, recurso, comando o evidencia y resultado.
- Abre una fila en `incidencias/REGISTRO.md` si surge un fallo nuevo; referencia su ID desde otros archivos.
- Nunca pegues tokens, claves privadas ni contraseñas en la documentación. El material local reside en `privado/` y no forma parte de los entregables.

## Comprobación rápida de acceso

```bash
./aws/infraestructura/academy-aws sts get-caller-identity
az account show
./nexoandes comprobar --nube gcp
```

Estos comandos son consultas de identidad o acceso. Antes de usarlos, sigue las instrucciones específicas de cada `ACCESO.md`. El usuario autorizó inventario, diseño, implementación y pruebas el 04/11/2026. Las credenciales y la configuración permanecen privadas; las consultas actuales de GCP usan su cuenta de servicio existente.
