# NexoAndes · Diseño multicloud (AWS + Azure + OCI)

> **Estado del documento:** diseño preliminar, 01/10/2026.
> **Fuente visual histórica:** la captura PNG y el `.excalidraw.bak` junto a este archivo muestran el diseño anterior con OCI. El [editable de trabajo](../../diagramas/excalidraw/nexoandes-multicloud.excalidraw), que ya incorpora GCP, se trasladó el 04/11/2026 a `diagramas/excalidraw/`; este texto histórico aún no se ha actualizado a ese diseño.
> **Uso:** es la fuente de verdad para escribir `integracion/CONTRATO.md`, `Plan-Maestro.md` y los planes `aws/PLAN.md`, `oci/PLAN.md` y `azure/PLAN.md`.

---

## 1. Resumen

NexoAndes publica un portal informativo de catálogo (Apache detrás de un balanceador) en **AWS Academy**, que ya está implementado y verificado el 30/09/2026. Para el Entregable 2 se amplía a **tres nubes**:

- **AWS** sigue siendo el centro: aloja la aplicación y la base de datos primaria (PostgreSQL).
- **OCI (Always Free)** aloja una **réplica de PostgreSQL** y la **copia 1 de los respaldos**, con gasto cero.
- **Azure (Azure for Students)** aloja la **copia 2 de los respaldos** y la vista de monitoreo y costos.
- Las nubes se conectan con **túneles IPsec** cuyo centro es la Virtual Private Gateway de AWS.

Lo que existe hoy es solo AWS. Azure y OCI son **diseño previsto, no desplegado**, y así debe decirse en cualquier documento.

## 2. Cómo leer el diagrama

| Elemento | Significado |
|---|---|
| Recuadro naranja | AWS Academy |
| Recuadro azul punteado | Azure for Students |
| Recuadro rojo punteado | OCI Always Free |
| Flecha azul continua | Flujo web verificado (usuario → internet → ALB → servidores) |
| Flecha gris punteada | Conectividad técnica probada (aplicación → base de datos, TCP 5432) |
| Flecha rosa punteada | Diseño previsto o función pendiente (VPN, replicación, respaldos) |
| Texto rosa pequeño | Aclaración de lo no probado o pendiente |
| Recuadro inferior | Supuestos y límites de cada cuenta |

## 3. Estado de cada pieza

| Nube | Pieza | Estado |
|---|---|---|
| AWS | VPC, subredes, IGW, NAT, ALB, Target Group, ASG, EC2 Apache, EC2 PostgreSQL, Security Groups | Implementado y verificado (30/09/2026) |
| AWS | Conectividad TCP 5432 de las apps a la base de datos | Probada |
| AWS | Bucket S3 | Existe con 0 objetos; el respaldo real está pendiente |
| AWS | 2 alarmas de CloudWatch | Existen; el disparo no se ha probado |
| AWS | Virtual Private Gateway y VPN | Gateway creada y confirmada viable en el Learner Lab (`vgw-0e36df7fa8f7033e1`, 01/10/2026). Falta Customer Gateway, conexiones Site-to-Site y pruebas con OCI/Azure |
| AWS | HTTPS, SSH restringido, secretos, cifrado de respaldos | Pendientes |
| OCI | Todo | Diseño previsto, no desplegado |
| Azure | Todo | Diseño previsto, no desplegado |

## 4. Límites de las cuentas (el diseño debe respetarlos)

### AWS Academy (Learner Lab)
- Sesiones de 4 horas; las credenciales son temporales y cambian en cada sesión.
- Solo se puede usar el rol `LabRole` / `LabInstanceProfile`; no se crean usuarios IAM.
- Presupuesto de USD 50–100 según el curso.
- Máximo 9 instancias, EC2 de nano a large, EBS hasta 100 GB. RDS no se usó por restricción del lab.
- **Site-to-Site VPN no figura en la lista de servicios que revisé** (la lista puede estar desactualizada). Hay que probar si se puede crear una Virtual Private Gateway.
- La VPN gestionada cuesta USD 0.05 por hora y por conexión.

### Azure for Students
- USD 100 de crédito por 12 meses, sin tarjeta de crédito.
- No cubre ExpressRoute, Azure DevOps ni Marketplace.
- Los créditos de cada mes no se acumulan.
- Con 90 días sin uso pueden borrar los recursos de cómputo.
- El VPN Gateway cobra por hora; el precio del SKU está **por verificar** en la calculadora de Azure.

### OCI Always Free (gasto cero)
- 2 VM AMD micro (1/8 OCPU, 1 GB) **o** Ampere A1 hasta 2 OCPU y 12 GB en total.
- 200 GB de almacenamiento en bloque (arranque + volúmenes), solo en la región home.
- 20 GB de Object Storage y 50 000 peticiones al mes.
- 2 VCN, Bastion, Monitoring y Notifications; 10 TB de salida de datos al mes.
- Las instancias con CPU, red y memoria por debajo de 20 % durante 7 días pueden ser reclamadas.
- **No se usan** DRG, CPE, Alarms ni IP pública reservada, porque la documentación no los lista como Always Free.
- No se hace "Upgrade to Pay As You Go".

## 5. AWS en detalle (implementado)

**Red:** VPC `10.10.0.0/16` en `us-east-1`.

| Subred | CIDR | Zona | Contenido |
|---|---|---|---|
| Pública A / B | 10.10.1.0/24 y 10.10.2.0/24 | A y B | Internet Gateway, ALB, NAT Gateway |
| Privada de aplicación A | 10.10.11.0/24 | us-east-1a | EC2 Apache A |
| Privada de aplicación B | 10.10.12.0/24 | us-east-1b | EC2 Apache B |
| Privada de datos | 10.10.20.0/24 | una sola zona | EC2 PostgreSQL 15 primario |

**Camino de una petición web:** usuarios → Internet → Internet Gateway → Application Load Balancer (HTTP 80) → Target Group (2 destinos saludables) → EC2 Apache en la zona A o B.

| Componente | Qué hace | Por qué está |
|---|---|---|
| Internet Gateway | Entrada y salida a Internet de las subredes públicas | Publicar el portal |
| Application Load Balancer | Reparte tráfico HTTP entre los servidores | Disponibilidad y punto único de entrada |
| Target Group | Lista de servidores sanos | El ALB solo envía a los saludables |
| Auto Scaling Group | Mínimo 2, máximo 4, deseado 2 (plantilla v2); reemplaza instancias caídas | Escalabilidad y recuperación automática |
| EC2 Apache A y B | Sirven el portal NexoAndes en dos zonas | Tolerancia a la falla de una zona |
| NAT Gateway | Salida a Internet de las subredes privadas (actualizaciones) | Los servidores no tienen IP pública |
| EC2 PostgreSQL 15 | Base de datos primaria, con volumen EBS (hasta 100 GB) | RDS no está permitido en el lab |
| Security Groups | SG-ALB, SG-App (TCP 80 solo desde SG-ALB), SG-DB (TCP 5432 solo desde SG-App) | Mínimo privilegio entre capas |
| S3 | Bucket de respaldos, hoy vacío | Respaldo pendiente |
| CloudWatch | 2 alarmas (disparo no probado) | Monitoreo |
| LabRole / LabInstanceProfile | Único rol disponible | Restricción del lab |

## 6. OCI en detalle (diseño previsto, gasto cero)

**Red:** VCN `10.30.0.0/16`, subred `10.30.1.0/24`, dentro del compartment `nexoandes` en la región home.

| Componente | Qué hace | Por qué está en OCI |
|---|---|---|
| VM Ampere A1 (2 OCPU, 12 GB) | Aloja la réplica de PostgreSQL y el extremo IPsec | Es el cómputo más grande que se puede tener gratis y de forma permanente. La AMD micro (1 GB) es muy justa para PostgreSQL |
| PostgreSQL réplica | Copia en streaming de la base primaria | Continuidad si falla la zona o la base de AWS |
| strongSwan (en la misma VM) | Extremo IPsec hacia la Virtual Private Gateway de AWS | Evita DRG y CPE, que no constan como gratis. Como la réplica vive en la misma VM, no hace falta reenviar tráfico |
| Object Storage (20 GB) | Copia 1 de los respaldos | Almacenamiento gratis y permanente; exige retención corta para no pasar el límite |
| NSG | UDP 500/4500 solo desde AWS; SSH solo por Bastion | Mínimo privilegio |
| Bastion | Acceso SSH sin exponer el puerto 22 | Es un servicio gratuito |
| Monitoring | Métricas de la VM y del disco | Vigilancia sin Alarms |

**Cuidados propios de OCI**
- La VM necesita la **IP pública efímera** que trae para que AWS tenga un destino. Si se elimina la VM, esa IP se pierde y hay que actualizar el lado de AWS.
- La capacidad de la A1 puede estar agotada ("Out of capacity"). Plan B: VM AMD micro, con las limitaciones de memoria.
- Para evitar el reclamo por inactividad hay que mantener actividad real (replicación continua y tareas periódicas).
- La región home se elige al registrarse y no se cambia después.

## 7. Azure en detalle (diseño previsto)

**Red:** VNet `10.20.0.0/16` con `GatewaySubnet`, dentro de un Resource Group de una suscripción.

| Componente | Qué hace | Por qué está en Azure |
|---|---|---|
| VPN Gateway + IP pública estática | Extremo IPsec hacia AWS | Interconexión privada con la nube principal |
| Blob Storage (LRS, nivel cool) | Copia 2 de los respaldos cifrados | Segunda copia en otro proveedor, barata |
| Azure Monitor (Log Analytics) | Vista consolidada de métricas y alertas | Monitoreo multicloud; el costo de ingesta está por verificar |
| NSG | UDP 500/4500 y TCP 5432 solo desde AWS | Mínimo privilegio |
| Cost Management | Alertas de presupuesto al 50 % y 80 % de USD 100 | Proteger el crédito |

**Cuidado principal:** el VPN Gateway cobra por hora encendido. Se crea para pruebas y para la sustentación, y se borra después.

## 8. Interconexión

```
        Azure  ──── VPN #1 (IPsec) ────┐
                                       ▼
                         Virtual Private Gateway (AWS)
                                       ▲
        OCI    ──── VPN #2 (IPsec) ────┘
```

- **AWS es el centro.** Azure y OCI se conectan a la Virtual Private Gateway; el diseño no prevé un túnel directo entre Azure y OCI.
- **Lado AWS:** Virtual Private Gateway, un Customer Gateway por cada nube remota y dos conexiones Site-to-Site, con propagación de rutas a las subredes privadas.
- **Lado OCI:** strongSwan en la VM Ampere, sin DRG ni CPE.
- **Lado Azure:** VPN Gateway y Local Network Gateway con la IP de AWS.
- **Plan B si el Learner Lab no permite la Virtual Private Gateway:** strongSwan en una EC2 como extremo IPsec de AWS.
- **Costo:** AWS cobra USD 0.05 por hora y por conexión; Azure cobra el gateway por hora. OCI no cobra. Las claves precompartidas nunca se escriben en archivos versionados.

| Red | CIDR |
|---|---|
| AWS VPC | 10.10.0.0/16 |
| Azure VNet | 10.20.0.0/16 |
| OCI VCN | 10.30.0.0/16 (subred 10.30.1.0/24) |

Los rangos son una propuesta y no se solapan.

## 9. Datos y respaldos

- **Replicación:** de la base primaria en AWS a la réplica en OCI, por el túnel IPsec, con PostgreSQL en streaming (misma versión mayor, TLS, usuario de replicación dedicado, `pg_hba` limitado a la IP del primario). TCP 5432 solo desde `10.30.1.0/24` hacia la base de AWS.
- **Regla de 3 copias:** la base primaria; la copia en S3 (pendiente; hoy 0 objetos); la copia 1 en OCI Object Storage; la copia 2 en Azure Blob.
- **Retención:** el límite de 20 GB de OCI obliga a rotar respaldos.
- **Prueba obligatoria:** restaurar un respaldo en otra instancia y promover la réplica a mano.
- **Decisión abierta:** cómo llega el respaldo a Blob y a Object Storage, por el túnel o por el endpoint público con firewall e identidad mínima.

## 10. Seguridad

| Control | Estado |
|---|---|
| Servidores en subredes privadas, sin IP pública | Implementado en AWS |
| Security Groups por capa (ALB → App → BD) | Implementado en AWS |
| IAM mínimo (solo LabRole) | Por restricción del lab |
| NSG mínimos en Azure y OCI | Diseño |
| Túnel IPsec entre nubes | Diseño |
| Alertas de presupuesto en Azure | Diseño |
| HTTPS en el ALB | **Pendiente** (hoy HTTP 80); falta comprobar si el lab permite un certificado |
| SSH público | **Pendiente de restringir** |
| Manejo de secretos | **Pendiente** |
| Cifrado en reposo (EBS, S3, Blob, Object Storage) | **Pendiente** |
| Disparo de alarmas | **Pendiente de probar** |

## 11. Resiliencia y puntos únicos de falla

| Falla | Qué pasa hoy | Qué cubre el diseño |
|---|---|---|
| Cae un servidor web | El ASG lo reemplaza; el ALB envía al otro | Cubierto en AWS (falta probar el reemplazo y dejar evidencia) |
| Cae una zona de AWS | La otra zona sigue sirviendo el portal | Web cubierta; **la base de datos está en una sola zona** |
| Cae la base primaria | No hay failover automático | La réplica de OCI permite promoción **manual** (por probar) |
| Se pierden los respaldos de AWS | Hoy no hay respaldos reales | Copias en OCI y Azure (por implementar) |
| Cae el túnel VPN | Se detiene la replicación | La aplicación sigue funcionando; hay que vigilar el retraso |
| OCI reclama la VM por inactividad | Se pierde la réplica | Mantener actividad real |

**SPOF principal:** la base de datos PostgreSQL en una sola zona. Las metas de RPO y RTO son una **propuesta por validar** y deben definirse en el contrato.

## 12. Costos

| Nube | Presupuesto | Qué puede costar | Control |
|---|---|---|---|
| AWS | USD 50–100 según el curso | VPN gestionada (USD 0.05 por hora por conexión), NAT, instancias | Apagar la VPN al terminar cada prueba; revisar el gasto del lab |
| Azure | USD 100 | VPN Gateway por hora, Log Analytics | Alertas al 50 % y 80 %; borrar el gateway tras cada prueba |
| OCI | USD 0 | Nada, si solo se usan recursos Always Free | No subir de cuenta; revisar Cost Analysis |

## 13. Decisiones abiertas y supuestos

1. ~~¿El Learner Lab permite la Virtual Private Gateway?~~ **Resuelto (01/10/2026): sí.** Se creó `vgw-0e36df7fa8f7033e1` sin restricción. No hace falta el Plan B de strongSwan en EC2 para el lado AWS.
2. **¿Hay capacidad de la A1 en la región home de OCI?** Si no, plan B con AMD micro.
3. **Precio y SKU del VPN Gateway de Azure.** Por verificar en la calculadora.
4. **Cómo llegan los respaldos a Blob y a Object Storage** (túnel o endpoint público).
5. **Metas de RPO y RTO.** Propuesta por validar.
6. **¿Funciona HTTPS en el Learner Lab?** Por verificar (certificado importado o alternativa).
7. **Reparto de funciones entre nubes.** Es una propuesta de diseño y hay que confirmarla.
8. **Los rangos CIDR** de Azure y OCI son propuestos.

## 14. Qué respalda cada rúbrica

| Rúbrica | Cómo ayuda este diseño |
|---|---|
| Entregable 1, criterio 2 (arquitectura y red) | Diagrama, CIDR, subredes, puertos y flujos |
| Entregable 1, criterio 3 (proveedores y servicios) | Reparto por nube y límites de cada cuenta; Azure y OCI marcados como diseño |
| Entregable 2, criterio 1 (evolución V1→V2) | Lo que se agrega: réplica, respaldos, VPN, seguridad |
| Entregable 2, criterio 3 (controles de seguridad) | Sección 10 y las brechas por cerrar |
| Entregable 2, criterio 4 (escalabilidad y resiliencia) | Sección 11 y el SPOF de la base de datos |
| Entregable 2, criterio 5 (evidencias) | Solo AWS es verificable hoy; el resto depende de la implementación |

Las evidencias (capturas de consola y navegador) las toma una persona y no se simulan.

## 15. Fuentes consultadas

- Documentación de AWS Academy Learner Lab (servicios permitidos y límites) y página de precios de AWS VPN.
- Recursos Always Free de Oracle Cloud: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
- Oferta Azure for Students y documentación de SKU del VPN Gateway de Azure.

Los precios y límites pueden cambiar; vuelve a verificarlos antes de implementar.
