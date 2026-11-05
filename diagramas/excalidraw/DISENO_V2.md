# NexoAndes V2 — diseño de continuidad

Fecha: 04/11/2026. Autorización: el usuario pidió proceder con inventario, diseño, implementación viable y pruebas. El editable principal sigue siendo `nexoandes-multicloud.excalidraw`; este archivo explica las decisiones y sus límites.

## Objetivo y límites

- AWS Academy: portal en dos zonas mediante ALB/ASG y PostgreSQL 15 privado. Reutilizar LabInstanceProfile y los recursos persistentes; no reemplazar la base ni su volumen.
- Azure: copia independiente de respaldos mediante el endpoint HTTPS autenticado. Mantener VPN Gateway y monitoreo ampliado como opcionales. No modificar las cargas ajenas a NexoAndes.
- GCP: una e2-micro con CPU compartida, disco estándar de arranque de 10 GB y disco estándar independiente de datos de 20 GB. SSH únicamente desde la IP administrativa autorizada. Cómputo pequeño sujeto a pruebas; los US$10 mensuales son crédito declarado, no saldo verificado.
- Transporte de réplica: IPsec strongSwan entre un gateway EC2 público dedicado y la VM GCP. PSK aleatoria entregada por canal administrativo; fuera de Terraform, user-data, dibujos y evidencias públicas.
- Los respaldos siguen una ruta HTTPS independiente de la VPN. La copia no sustituye a la restauración.

## Comportamiento previsto

1. Operación normal: usuarios → ALB → dos EC2 web → PostgreSQL AWS. Una sonda `/health` permite demostrar la conexión a la BD con datos sintéticos, sin implementar pedidos ni inventario de negocio.
2. Caída web: el ALB retira el destino no saludable y el ASG repone capacidad. Se probarán caída de proceso y recuperación, diferenciándolas de escalado por carga.
3. Caída de la BD: aislar y detener el primario AWS, comprobar el último marcador recibido por GCP, promover manualmente la réplica y cambiar el destino de las sondas de aplicación. No promover por la mera pérdida de conectividad.
4. Caída completa de AWS: la VM GCP sirve un portal mínimo y la sonda mediante su dirección pública independiente. El cambio de URL es manual; no se declara failover DNS automático ni continuidad transparente para usuarios.
5. Retorno: detener las escrituras de la demostración, conservar un respaldo del primario promovido, resincronizar AWS antes de devolver el rol y verificar consistencia. No arrancar dos primarios aceptando escrituras divergentes.
6. Fin de la sesión: retirar la capa temporal de AWS y detener GCP conservando sus discos. La réplica detenida no recibe cambios. El laboratorio no ofrece alta disponibilidad permanente cuando la sesión está inactiva.

## Aceptación y pruebas

| Prueba | Resultado requerido |
|---|---|
| Acceso web | HTTP 200 del portal y sonda con lectura PostgreSQL |
| Seguridad | SSH restringido; BD sin exposición pública; PSK y contraseñas fuera de documentación |
| Fallo web | Continuidad desde el otro destino, retirada del destino fallido y reposición |
| Escalabilidad | Aumento real de capacidad provocado por carga, con actividad del ASG y métricas; tener una política no basta |
| Réplica | Marcador escrito en AWS visible en GCP en recuperación; estado de streaming comprobado |
| Failover manual | Primario anterior aislado; promoción GCP, lectura y escritura sintéticas correctas; duración y datos recuperados medidos |
| Restauración | Crear una base temporal desde el dump y comprobar el marcador; comparación SHA256 adicional |
| Apagado | Conservación de datos y respaldos; ausencia de recursos temporales que deban retirarse |

RTO y RPO son resultados por medir, no garantías. Los escenarios de 100/500/1000/5000 usuarios de la plantilla son análisis de crecimiento; no se atribuirá esa capacidad a las VMs sin mediciones.

## Riesgos aceptados y pendientes

- BD AWS y NAT en una zona; gateway IPsec único; VM GCP única. La solución no elimina todos los SPOF ni promete disponibilidad continua de producción.
- Cómputo de GCP reducido, respaldos sujetos a retención y almacenamiento total. El consumo de IPv4, tráfico y otras cargas comparte la cuenta de facturación.
- AWS Academy puede detener recursos al finalizar sesión. Las credenciales temporales y el saldo del laboratorio condicionan la operación.
- El inventario inicial encontró el ASG sin instancias y con lanzamientos cancelados; se debe resolver antes de acreditar alta disponibilidad actual.
- El inventario inicial encontró Cloud Billing API deshabilitada en GCP. El costo consultado de Azure no informa por sí solo el crédito restante.
- La aplicación de demostración usa datos sintéticos. La disponibilidad del portal informativo original no prueba por sí misma disponibilidad de datos.

El estado final y los resultados reales se registrarán en `ESTADO_2026-11-04.md`, en los AVANCES de cada nube y en las evidencias, sin convertir pruebas pendientes en éxitos.
