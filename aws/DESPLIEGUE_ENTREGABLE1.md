# Despliegue y verificación de la Arquitectura V1

Esta guía acompaña el [informe](../entregables/entregable-01/INFORME.md). El portal ya se publicó por SSM en las instancias web y en la versión 2 del Launch Template; `curl` obtuvo HTTP 200. El número real de equipo y las capturas del navegador siguen pendientes. Renueva las credenciales si el laboratorio expiró.

## Datos que faltan antes de publicar

- Confirmar con el equipo la empresa ficticia y el número real. Actualiza `TEAM_NUMBER="XX"` en `user-data.sh` y ejecuta `./aws/infraestructura/publicar-portal.sh NUMERO_EQUIPO` desde la raíz del repositorio.
- Confirmar la cuenta y región con STS antes de cualquier cambio. No copiar tokens a scripts ni al informe.

## Secuencia operativa

1. **Inventario de solo lectura:** comprobar VPC, ASG, plantilla de lanzamiento, ALB, Target Group, listener, instancias y capacidad SSM. Comparar IDs con `infraestructura/infra-params.env`; no ejecutar scripts de creación si los recursos ya existen.
2. **Ruta de tráfico:** el ASG ya está asociado al Target Group y dos destinos quedaron saludables (INC-005). Vuelve a comprobarlo con cada nueva sesión.
3. **Publicar cambios del equipo:** ejecuta `./aws/infraestructura/publicar-portal.sh NUMERO_EQUIPO` desde la raíz. El script comprueba cuenta, asociación y estado antes de actualizar las instancias y la plantilla.
4. **Comprobar:** abre el DNS del ALB, verifica NexoAndes y el número de equipo, recarga varias veces y registra las instancias/zona respondidas. Guarda URL, fecha y resultado.
5. **Evidencia del informe:** guarda las capturas E01–E05 en `../entregables/entregable-01/evidencias/`. No se han tomado por el agente; deben ser capturas reales del laboratorio por el usuario.

## Consultas iniciales

```bash
./aws/infraestructura/academy-aws sts get-caller-identity
./aws/infraestructura/inventario-lectura.sh
```

Si AWS indica `ExpiredToken`, renovar credenciales en Vocareum antes de continuar. Si SSM no administra las instancias, determinar un método de actualización autorizado después del inventario; no abrir SSH a Internet para facilitar el despliegue.
