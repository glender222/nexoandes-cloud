# Capturas de Unidad 2 — Arquitectura V2

Ya se insertaron en el Word seis capturas existentes: tres históricas del Entregable 1 y tres del 04/11 (portal AWS, portal GCP y sesión Supabase). El usuario puede añadir o sustituir fotografías específicas de consola; las existentes se conservan con su fecha y procedencia. Esta guía se actualizó con el inventario del 04/11/2026 23:01 Lima y Studio probado a las 23:33. No afirma que todos los recursos sigan encendidos: GCP estaba detenido; Azure mantiene almacenamiento, no una VM del proyecto.

## Antes de capturar

Confirmar cuenta AWS 849533029543/us-east-1, grupo Azure nexoandes-lab/northcentralus y proyecto GCP gen-lang-client-0623826791/us-central1. `./nexoandes comprobar` valida acceso, no inicia servicios. Actualizar el estado antes de fotografiar; una IP/DNS efímera de una sesión anterior no es una URL vigente garantizada.

Portal del último corte: [HTTPS](https://nexoandes-alb-409538740.us-east-1.elb.amazonaws.com/), [login](https://nexoandes-alb-409538740.us-east-1.elb.amazonaws.com/acceso/), [Studio](https://nexoandes-alb-409538740.us-east-1.elb.amazonaws.com:8443/). Certificado académico autofirmado. Las credenciales están en archivos privados del proyecto; **no fotografiar contraseñas, tokens ni claves API**. En Studio usar Overview/Table Editor, no Settings/API Keys.

## Fotos y ubicación

Guardar en `entregables/entregable-02/evidencias/`.

| Archivo propuesto | Qué fotografiar | Ubicación / prueba |
|---|---|---|
| V2-E01-alb-asg.png | ALB, TG nexo- con dos healthy en zonas distintas; ASG nexoandes-web 2–4 | Sección 17, Mejora 01; dos destinos no prueban por sí solos crecimiento 2→4 |
| V2-E02-sg-red.png | Subredes privadas y reglas de PG15/Supabase; incluir origen GCP por ruta privada y SG app/ALB | Mejora 02; no reducir regla de PG15 a «solo app» si también autoriza GCP |
| V2-E03-backups-azure.png | Storage nxa1db87b28407f → contenedor postgresql, dumps y configuración versionado/ciclo de vida | Mejora 03; no buscar VPN Gateway/IP pública Azure inexistentes ni etiquetar versión como inmutabilidad |
| V2-E03-hashes-restore.png | Resultados JSON/terminal de respaldos.json y restauracion-ciclo.json, con objeto y hashes/filas | Complemento Mejora 03; siete filas, ID máximo 39 |
| V2-E04-escalado.png | Historial ASG y métrica RequestCountPerTarget en la ventana UTC del ensayo | Mejora 04; usar escalabilidad.json para ubicar fecha. El ensayo CPU no acredita ese crecimiento |
| V2-E05-gcp-replica.png | VM y discos GCP, bucket; evidencia técnica de pg_is_in_recovery durante una sesión activa preparada | Mejora 05; VM detenida no demuestra streaming en marcha |
| V2-E05-failover.png | Resultados de failover.json y consistencia-retorno.json mostrando promoción/retorno y datos | Complemento Mejora 05; indicar ensayo del 04/11, sin prometer failover DNS automático |
| V2-E06-supabase.png | Login del portal y acceso privado autorizado; prueba negativa 401 sin sesión | Mejora 06; usuario sintético, sin mostrar contraseña ni tokens |
| V2-E06-studio.png | Studio HTTPS 8443 y proyecto cargado; prueba sin credenciales 401 | Mejora 06; credenciales del dashboard distintas de usuario Auth; no mostrar API Keys |

## Cómo presentar antes/después

Para «antes» usar fotos históricas originales o la figura V1, identificada como diagrama. No apagar/reconfigurar recursos para fabricar una captura antigua. ALB/ASG y segmentación ya existían en V1: describir la mejora efectiva de política/prueba, no afirmar que V1 tenía una sola web pública.

Para métricas de ensayos anteriores seleccionar la ventana exacta indicada en el JSON; una gráfica actual plana no refuta ni demuestra la prueba histórica. Si no se puede recuperar el historial, incluir el resultado técnico fechado y señalarlo como evidencia del ensayo, sin simular la consola.

GCP detenido puede fotografiarse como **estado de pausa**. Para demostrar réplica activa se requiere una sesión de continuidad preparada y su comprobación; no promover una base ni ejecutar fallos únicamente para tomar una foto. `./nexoandes continuidad` arranca recursos y consume crédito; usarlo solo para la demostración acordada.

## Pie de cada imagen

Indicar fecha/hora y zona horaria, nube/cuenta/proyecto, servicio/configuración, procedimiento y resultado observado. Distinguir figura, consulta de inventario, captura de estado actual y resultado de un ensayo anterior. Sustituir el marcador Equipo XX antes de la foto final del portal según los datos reales del equipo. Conservar las reservas del informe hasta insertar las fotos.

## IAM básico verificado — 05/11/2026

Capturar los controles reales siguiendo [integracion/IAM.md](../../integracion/IAM.md#capturas-para-el-entregable): AWS LabRole y perfil EC2; Azure, asignación Storage Blob Data Contributor en el contenedor postgresql; GCP, permisos del bucket y cuenta de servicio de las herramientas. Adjuntar evidencia JSON de copias y hashes. No mostrar claves, contraseñas ni tokens; MFA no está verificado.
