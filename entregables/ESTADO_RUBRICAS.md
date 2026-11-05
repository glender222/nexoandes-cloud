# Estado de entregables y pendientes — actualización IAM 05/11/2026

Se actualizaron los informes V1/V2 y su trazabilidad con las evidencias existentes. El usuario tomará las fotos. La revisión documental del 04/11 no operó cloud. La ampliación IAM del 05/11 creó una asignación RBAC en Azure y repitió pruebas de identidad y respaldos; no cambió el cómputo. Referencias de estado: inventario del 04/11 a las 23:01 Lima y publicación/pruebas Studio 23:33; son cortes fechados, no monitoreo en vivo.

## Resumen por unidad

| Entregable | Documentación actualizada | Evidencia existente | Falta cerrar |
|---|---|---|---|
| Unidad 1 / V1 | 20 títulos oficiales, base AWS, proveedores/modelos, red y SPOF; figura original y E01–E05 preservados | Recreación de la base del 22/10, funcionamiento, backup/restauración y persistencia | Fotos E01–E05 y datos finales de portada/portal; confirmar presentación del equipo |
| Unidad 2 / V2 | Comparación honesta, mapa V2, seguridad/STRIDE/NIST, IAM con límites, disponibilidad, DR y costos preliminares | Escalado 2→4, reposición, seguridad, PG15 DR/restore, Auth, persistencia y Studio externo | Fotos antes/después y mejoras/pruebas indicadas abajo; IAM básico actualizado el 05/11; completar valoración económica de las tres nubes |

No se asigna una nota ni se declara 20/20. Los cinco criterios de cada rúbrica se revisan en `entregable-01/REVISION_RUBRICA.md` y `entregable-02/REVISION_RUBRICA.md`.

## Implementación y pruebas que ya existen

| Área | Acreditado | Límite |
|---|---|---|
| Web AWS | ALB/ASG dos zonas; 2→4 por solicitudes; reposición con HTTP 200 observado | No demuestra 5.000 usuarios ni corrección de un fallo común de software |
| PG15 | Privado, persistencia, réplica AWS–GCP, promoción/retorno y restauración de copias | DR manual; VM GCP detenida no replica; NAT/gateway/primario únicos |
| Supabase | Auth y endpoint protegido; seis servicios; reinicio persistente; bootstrap web; Studio HTTPS 8443 con 401/200 | Una VM; PG17/Auth no se replica a GCP; restauración solo selectiva auth.users |
| Azure/GCP objetos | Copias privadas/versionadas, SHA256 coincidente y restauraciones PG15 | Versionado no es WORM; transferencias entre nubes bajo demanda |
| Seguridad/monitoreo | SG, SSM, IMDSv2, cifrado en reposo, IPsec y TLS académico; CloudWatch | IAM básico verificado el 05/11; sin mínimo privilegio integral, TLS interno completo ni alertas a personas |

## Tabla de pendientes

| ID | Qué falta | Tipo / prioridad | Acción y criterio de cierre | Responsable |
|---|---|---|---|---|
| P01 | Fotos finales V1 y V2 | Parcial: seis capturas existentes insertadas en Word el 05/11 | Ya están las tres fotos V1 correspondientes y portal AWS/GCP/Auth. Las pruebas se enlazan a registros; añadir fotos específicas ASG, copias e IAM si se requieren. No simular fotografías de consola | Usuario/equipo |
| P02 | Datos de portada y nombre/número de equipo en portal | Presentación / alta | E1 conserva campos por definir; E2 conserva los datos de su portada previa para revisión. Resolver el marcador XX antes de la foto final, sin inventar datos | Usuario/equipo |
| P03 | IAM básico implementado y verificado el 05/11 | Cerrado en alcance básico | Cinco perfiles EC2/IMDSv2; políticas y confianza LabRole exportadas; prueba de rol/S3; RBAC Azure al contenedor y copias con Entra; permisos GCP y hashes comprobados. [Detalle y límites](../integracion/IAM.md). MFA y mínimo privilegio integral quedan como mejora, no se afirman realizados | Operador cloud |
| P04 | Recuperación integral de Supabase | Fuera del trabajo activo por decisión del usuario — 05/11 | No se realizará este ensayo en el alcance actual. Se conserva como limitación: solo se probó restauración selectiva de auth.users; no afirmar recuperación integral del SaaS | No ejecutar en el alcance actual |
| P05 | Alarmas propias de memoria/disco/servicios Supabase | Implementación pendiente / media | Definir métricas/umbrales, desplegarlas y probar estados con consumo acotado | Operador cloud |
| P06 | Notificaciones a personas | Implementación pendiente / media | Definir canal y destinatario con el usuario antes de habilitar envíos; probar entrega y registrar evidencia | Usuario + operador |
| P07 | Operación GCP independiente de AWS | Verificación/implementación pendiente / media | Validar consola/IAP u otro acceso independiente autorizado. El ensayo actual usa el gateway AWS | Operador cloud |
| P08 | Cotización multicloud y saldo/vencimiento | Datos económicos / alta documental | Modelo AWS preliminar disponible. Completar Azure/GCP, tráfico/objetos y consumos; comprobar créditos en las consolas del titular | Usuario + equipo |
| P09 | Copias off-site autónomas sin herramientas de desarrollo | Mejora futura / media | Mover su ejecución programada a un servicio cloud y probarla sin sesión local; por ahora son copias bajo demanda, no tráfico de la aplicación | Operador cloud |
| P10 | TLS públicamente confiable y cifrado interno/GCP | Mejora de seguridad / según alcance final | Definir dominio/certificado y trayectos por proteger; probarlos. Se documenta la limitación académica actual | Equipo |
| P11 | Alta disponibilidad Auth y failover DNS automático | Mejora futura / según disponibilidad exigida | Diseñar con presupuesto/roles reales y ensayar fallo/retorno; no basta dibujar otro icono | Equipo |
| P12 | Pedidos, inventario y autorización/RLS comercial | Producto final / fuera del prototipo demostrado | Definir datos, flujos y permisos antes de exponer tablas comerciales | Equipo |

P05–P12 no se presentan como requisitos literales adicionales de las rúbricas ni como trabajo realizado. P03 está cerrado para IAM básico; su límite es el privilegio heredado del laboratorio y MFA no verificado. P04 queda fuera del trabajo activo por decisión del usuario del 05/11; la recuperación integral no está demostrada. No se exige agregar AD, RDS, WAF, Lambda o más iconos por cantidad; las decisiones se sustentan frente a los criterios y al alcance académico. Serverless aparece como contenido de unidad, pero no hay un despliegue serverless acreditado en este proyecto.

## Correcciones realizadas

Se retiraron afirmaciones no respaldadas de inmutabilidad, capacidad validada para 5.000 usuarios, cero costo GCP, eliminación total de SPOF, snapshots automáticos, roles/grupos ficticios, MFA auditado y monitoreo multicloud completo. Se conservaron los espacios de fotos y se vinculó cada prueba al archivo real. El plan de seguridad usa NIST CSF 2.0 como referencia, sin certificación o cumplimiento legal declarado.

Los costos están en `costos/estimacion.json` y se reproducen con `python3 entregables/costos/calcular.py`. Es un subtotal AWS con hipótesis explícitas y exclusiones; no una factura ni un total multicloud cerrado.
