# Revisión visual del mapa — 04/11/2026

Se revisó el editable detallado y se aplicó la simplificación solicitada. El mapa anterior `nexoandes-multicloud.excalidraw` permanece intacto. No se consultaron ni cambiaron recursos cloud; se conserva el inventario del 04/11/2026 a las 23:01 Lima.

## Hallazgos y correcciones

| Hallazgo | Cambio aplicado |
|---|---|
| Texto repetido: privado, desplegado, verificado, uso de Internet y servicios ya reconocibles | Descripciones retiradas; nombres y conexiones conservados. Cifras y pruebas operativas permanecen en la documentación. |
| Security Groups representados solo por una frase | Escudo Lucide junto a ALB, gateway, ASG web, PostgreSQL y Supabase; símbolo común en la franja de controles. Cada marca tiene `customData` con su recurso Terraform: alb, vpn, app, db o supabase. |
| Supabase y PostgreSQL con el mismo símbolo EC2 | Logotipos de producto de Simple Icons; se conserva la etiqueta EC2 para indicar autohospedaje. |
| Componentes de Supabase enumerados en un párrafo | Seis símbolos etiquetados: Auth, REST, PG17, Envoy, Studio y Meta. El candado agrupa la administración privada. |
| Tres servicios GCP como cajas solo de texto | PG15, IPsec y Portal con símbolos dentro de la única VM existente; pausa para su estado detenido. |
| Azure con iconos comunitarios | Storage Accounts y Virtual Networks del paquete oficial Microsoft Azure V24. |
| Versionado, retención y borrado como tarjetas explicativas | Iconos Lucide y cifras breves; leyenda para evitar símbolos ambiguos. |
| Pie del mapa con párrafos que repetían funciones del portal y las nubes | Leyenda breve de flujos y controles, y resumen de disponibilidad. |

## Qué se conservó deliberadamente como texto

Nombres de servicios, CIDR, zonas, puertos, tamaños de datos (20 GB, 40 GB y 10 + 20 GB), intervalos de respaldo/retención, estado detenido de GCP, TLS académico, operación de DR manual y ausencia de réplica Supabase. Son datos necesarios para interpretar el diseño; un icono por sí solo no los transmite.

El flujo naranja representa copias lógicas bajo demanda; no asegura copia autónoma entre proveedores. Las herramientas de desarrollo y la laptop quedan fuera de la topología del servicio. PostgreSQL 15 sigue separado de la base PG17 de identidad.

## Bibliotecas y significado

- AWS: paquete oficial local del usuario, versión 31/07/2026. Fuente y SHA256 en `bibliotecas/aws-oficial/FUENTE.json`.
- Azure: paquete oficial Microsoft V24. Origen y SHA256 en `bibliotecas/azure-oficial/FUENTE.json`.
- GCP: biblioteca comunitaria existente para logo, Compute Engine y Cloud Storage; autoría original en `bibliotecas/FUENTES.json`.
- Lucide: conceptos genéricos y controles. Commit fijado, archivos y licencia ISC en `bibliotecas/complementos/`. El escudo identifica Security Groups como una convención visual propia, **no** un icono oficial de AWS Shield, WAF o Network Firewall; esos servicios no se incorporaron al diseño.
- Simple Icons: marcas Supabase y PostgreSQL. Commit fijado y licencia CC0 conservados; marcas usadas solo para identificar productos. Las condiciones de marca de los titulares siguen siendo independientes.

Los SVG se incrustan por objeto dentro de Excalidraw. El archivo funciona sin conexión y conserva elementos editables para textos, grupos y flechas. Los originales descargados permanecen sin modificar; en el render se aplica color a `currentColor` de Lucide y a los logotipos monocromos de Simple Icons.

## Validación

Se contó el texto visible antes de editar: 472 palabras. El recuento y los objetos de la versión final se registran en `herramientas/validacion-visual.json`. Se comprobó importación con Excalidraw 0.18, recursos SVG incrustados, IDs únicos y grupos de seguridad; se exportaron PNG/SVG y se revisó visualmente el resultado. Los nombres de archivo de trabajo y el mapa original permanecen estables.

## Ajuste estructural Azure

Se sustituyó el bloque con símbolos sueltos por una jerarquía de contención: grupo `nexoandes-lab` → Storage Account LRS → contenedor Blob `postgresql`. El candado y «Privado» están dentro del contenedor. Versionado, borrado lógico de 7 días y retención de 14 días se agrupan bajo la cuenta de almacenamiento. La VNet es un recurso hermano de la cuenta, dentro del mismo grupo; no se dibuja una conexión privada Storage–VNet que no está implementada. Se mantiene «VPN Gateway deshabilitado».

Grupo de recursos, cuenta, contenedor y red usan SVG oficiales Microsoft. Cada nivel tiene un grupo editable propio y metadatos de relación; se validaron sus límites de contención. La flecha HTTPS termina en la cuenta de almacenamiento. No se consultó ni modificó Azure.

## Actualización de Studio externo

La entrada HTTPS ahora incluye 443 y 8443; el símbolo de clave en componentes Supabase indica Studio autenticado en 8443. La etiqueta anterior «Administración privada» se retiró al habilitar el acceso externo autorizado; postgres-meta y PostgreSQL conservan acceso interno. Publicación y pruebas en `integracion/SUPABASE.md`.

## Conectores y márgenes — 05/11/2026

Endpoint S3 reubicado dentro de la VPC y servicio S3 regional fuera de ella. La salida del endpoint termina hacia la derecha en S3; las entradas de respaldos terminan en el endpoint. Se separó la etiqueta Auto Scaling del borde, se corrigieron salidas ALB para no atravesar sus textos, se agruparon conexiones Auth y se evitó el cruce del respaldo Supabase con 40 GB. Exportaciones PNG/SVG y figura del Word sincronizadas. Se conserva el corte cloud fechado, sin operaciones de infraestructura. La relación gateway–S3 corresponde a `aws/terraform/network.tf`; referencia: https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints-s3.html.
