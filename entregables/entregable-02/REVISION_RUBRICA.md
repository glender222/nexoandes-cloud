# Revisión de rúbrica — Entregable 2

Revisión del 04/11/2026. Fuente: [rúbrica 2](../../referencias/rubrica%20entregable%202.md), cinco criterios de cuatro puntos. «Documentado» no significa «implementado» ni garantiza 4/4.

| Criterio | Estado y evidencias reales | Falta cerrar o justificar |
|---|---|---|
| 1. Evolución V1→V2, 2–6 | Comparación corregida: ALB/ASG ya existían; nuevas pruebas, réplica/copia y Supabase. Figuras V1/V2 enlazadas | Fotos antes/después con fecha y datos de portada/portal |
| 2. Amenazas/vulnerabilidades, 8 y 19 | Matriz STRIDE con control y riesgo residual; plan integral y correspondencia NIST CSF 2.0 en 7.1 | Validar tratamiento de riesgos pendientes; no afirmar certificación normativa |
| 3. Controles de seguridad, 7/9/10/14 | Red privada, SG, SSM, cifrado, IPsec, Auth y Studio 401/200; IAM básico: perfil AWS, asignación RBAC Azure al contenedor y permisos GCP comprobados (05/11, integracion/IAM.md) | Mínimo privilegio integral y MFA no acreditados; memoria/disco/avisos no implementados; TLS académico e interno HTTP declarados |
| 4. Escalabilidad/disponibilidad/fallos, 11–13 y 15 | Escalado 2→4, reposición, DR/retorno PG15 y restore con datos sintéticos | Sin prueba de 5.000 usuarios, failover automático o HA Auth; restauración integral Supabase pendiente; GCP depende del gateway para administración ensayada |
| 5. Evidencias/pruebas/documentación, 16–18 y 20 | Resultados vinculados a JSON, mapa V2 insertado, Studio externo documentado y costos reproducibles | Fotos originales del usuario; valoración Azure/GCP/tráfico y saldos aún sin cierre; revisar presentación final |

Las capturas no se generaron para sustituir las fotos del usuario. La [guía actualizada](GUIA_CAPTURAS.md) retira IP/DNS antiguos y recursos Azure inexistentes. La [tabla consolidada](../ESTADO_RUBRICAS.md) separa implementación, verificación y mejoras futuras.

El costo corregido es un modelo AWS parcial, no el antiguo total ficticio de US$43,58 ni una factura. Las cuotas, impuestos, créditos y beneficios gratuitos requieren verificación específica.

## Revisión del Word con capturas — 05/11/2026

El Word vigente se revisó visualmente y contiene imágenes en R01–R19 y tres bloques antes/después. Esto actualiza las referencias anteriores a reservas vacías: no se deben solicitar nuevamente todas las imágenes. R09 y R11 muestran configuración o recursos, mientras que los ensayos de escalado y continuidad se sustentan en sus registros; R16 presenta resultados de integridad/restauración. Las pantallas R17–R19 muestran costos en sus ámbitos y períodos y no cierran por sí mismas una cotización del proyecto multicloud. Quedan por confirmar los datos de portada, actualizar el índice en Word y decidir el tratamiento y responsables de riesgos. Detalle y orden de cierre: [PLAN_CIERRE_RUBRICA.md](PLAN_CIERRE_RUBRICA.md).
