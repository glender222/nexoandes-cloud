# Mapa de trabajo de NexoAndes

Este es el espacio compartido para ir ajustando la arquitectura del proyecto por unidad y entregable. El archivo principal es [nexoandes-multicloud.excalidraw](nexoandes-multicloud.excalidraw). Conserva los iconos, grupos, textos y conexiones del dibujo existente; los nuevos componentes se pueden tomar de [bibliotecas/](bibliotecas/).

## Nueva versión detallada — 04/11/2026

**Studio externo:** Supabase admite administración autenticada por HTTPS 8443 del ALB, publicada y probada el 04/11/2026 23:33. El mapa refleja esta entrada; metadatos y BD permanecen internos. [Acceso y pruebas](../../integracion/SUPABASE.md).

**Azure reorganizado:** grupo de recursos → cuenta Storage → contenedor Blob privado; políticas agrupadas bajo la cuenta y VNet separada como recurso hermano. Iconos oficiales y grupos editables por nivel.

**Simplificación visual:** se redujeron las explicaciones repetidas y se incorporaron símbolos para Security Groups, componentes Supabase/GCP, privacidad, versionado y retención. Análisis, criterios de selección y validación en [REVISION_VISUAL.md](REVISION_VISUAL.md).

**Rediseño con el paquete local del usuario:** se integraron 16 SVG oficiales desde la carpeta de Descargas indicada, con huellas verificadas. El nuevo diseño usa símbolos más grandes, dos columnas de disponibilidad AWS, subredes alineadas, un grupo ASG común a las web y almacenamiento/controles regionales fuera de las subredes. Se conservan Supabase como SaaS académico, el detalle de Azure/GCP y la exclusión de la laptop. El [origen de los iconos](bibliotecas/aws-oficial/README.md) y sus [huellas](bibliotecas/aws-oficial/FUENTE.json) quedan en el proyecto; el editable incluye todos los SVG y no depende de Descargas.

Para continuar la revisión visual usamos [nexoandes-multicloud-detallado.excalidraw](nexoandes-multicloud-detallado.excalidraw). Es un **segundo editable**: el mapa anterior y sus exportaciones se conservan sin cambios. Vista previa [PNG](nexoandes-multicloud-detallado.png) y exportación [SVG](nexoandes-multicloud-detallado.svg).

Esta versión reorganiza los componentes implementados, subredes/CIDR, zonas, puertos y flujos separados por color. Sitúa **Supabase como servicio SaaS académico del proyecto**, autohospedado en `app_b`, y distingue su PostgreSQL 17 del PostgreSQL 15 principal. La clasificación técnica de la plataforma como BaaS/PaaS se conserva en la guía Supabase; esta etiqueta describe el rol elegido para el proyecto, no un cambio de producto ni una certificación de la rúbrica.

**Revisión del 04/11/2026 23:01 America/Lima:** se confirmaron por API las identidades y recursos de las tres nubes. [Inventario de lectura](../../infraestructura/evidencias/inventario-mapa-20261104.json): AWS con dos web, PostgreSQL, Supabase y gateway EC2 en ejecución; VM GCP detenida, bucket existente; Azure con Storage y VNet del proyecto. El inventario acredita recursos y estado de cómputo, no una nueva prueba de funcionamiento de las aplicaciones.

El mapa ahora usa los [SVG oficiales de AWS](bibliotecas/aws-oficial/README.md), extraídos sin alterar del paquete local del usuario, versión 31/07/2026 y embebidos individualmente. Azure usa el [paquete oficial Microsoft V24](bibliotecas/azure-oficial/README.md); GCP conserva sus iconos comunitarios con autoría en [FUENTES.json](bibliotecas/FUENTES.json). Los controles genéricos y logotipos de producto se documentan en [complementos](bibliotecas/complementos/README.md). La captura del compañero no permite identificar la biblioteca o herramienta exacta que empleó; se adoptó la misma familia visual oficial de AWS.

Se eliminaron el equipo local y sus conexiones de la topología de servicio: es una herramienta de desarrollo/administración, no un servidor de NexoAndes. Las flechas naranjas representan **flujo lógico de copias bajo demanda**, no transferencia autónoma directa entre proveedores. El mecanismo implementado sigue siendo el script ejecutado desde herramientas de desarrollo; el timer local continúa deshabilitado. Se conserva este detalle operativo en `integracion/SUPABASE.md`, fuera del dibujo. IPsec y réplica PG15 están implementados/probados pero inactivos con GCP apagado; Supabase Auth no está replicado en GCP.

GCP desglosa los tres servicios dentro de una única VM: PostgreSQL standby, strongSwan y portal/sonda. Azure muestra grupo de recursos, Blob/contenedor, versionado/borrado lógico, política de ciclo de vida, VNet y GatewaySubnet. No se añadieron VMs ni gateways al dibujo sin implementación.

Validación: importación con el lector oficial de Excalidraw 0.18, exportación PNG/SVG e inspección visual. Tarjetas, textos y conexiones editables; los SVG AWS son objetos individuales, no una imagen plana de toda la arquitectura.

Abre el nuevo `.excalidraw` directamente en Excalidraw; los iconos ya están incluidos y no requiere importar las bibliotecas para verlo. Edita y guarda sobre **ese archivo** para mantener esta versión. El generador [herramientas/generar_mapa_detallado.py](herramientas/generar_mapa_detallado.py) documenta su construcción inicial; ejecutarlo de nuevo sobrescribe este segundo editable, por lo que no debe usarse después de realizar cambios manuales sin conservarlos primero. Los textos de los informes por unidad no se modificaron.

## Abrir y guardar

1. Abre [Excalidraw](https://excalidraw.com/) o tu editor compatible.
2. Usa **Abrir** para cargar `nexoandes-multicloud.excalidraw`.
3. En el panel **Biblioteca**, abre el menú e importa los archivos `.excalidrawlib` de `bibliotecas/` que necesites. Los archivos descargados están disponibles localmente; la importación se realiza en el editor o perfil que uses.
4. Edita y guarda sobre el mismo archivo principal. Si el navegador descarga otra copia, reemplaza este archivo con el resultado de la edición.

## Cómo mantendremos el mapa

- Usar primero los artefactos existentes y mantener un estilo coherente al añadir iconos de las bibliotecas.
- Distinguir diseño previsto, recurso desplegado y función probada. Una flecha VPN, una VM o un icono de respaldo no son evidencia de funcionamiento.
- Acompañar los cambios de estado con fecha y referencia a pruebas de `aws/`, `azure/`, `gcp/` o `integracion/`. No asumir disponibilidad actual a partir de verificaciones anteriores.
- Mantener separado el alcance de cada unidad: V1 para el Entregable 1 y V2 para el Entregable 2. Las exportaciones para cada documento se guardan en su carpeta de evidencias correspondiente.
- Usar AWS, Azure y GCP para el diseño actual. OCI queda como referencia histórica.
- No incluir claves, tokens, contraseñas ni otros secretos en el dibujo o las bibliotecas.

Después del traslado se actualizó el mapa con la implementación y las pruebas del 04/11/2026. Consulta el [estado comprobado](ESTADO_2026-11-04.md), el [diseño V2](DISENO_V2.md) y las exportaciones [PNG](nexoandes-multicloud.png) / [SVG](nexoandes-multicloud.svg). El presupuesto GCP indicado por el usuario es de **US$10 mensuales en créditos de desarrollador**; su saldo y vencimiento no se pudieron verificar por API. Las etiquetas de pruebas son evidencia fechada y no significan que los recursos permanezcan encendidos.

## Origen e historial

El 04/11/2026 se movió `referencias/oficial/nexoandes_multicloud(2).excalidraw` a esta ubicación. Se conservaron sus 721 elementos activos y el contenido idéntico byte a byte.

SHA-256 al trasladarlo: `8811d8ab5138f9686ba0af14718a863a227a338f25c55c1ab368c350532308c4`.

La [captura de octubre](../../referencias/oficial/Screenshot%20From%202026-10-01%2011-01-42.png) y el archivo `.excalidraw.bak` en `referencias/oficial/` son históricos y todavía muestran OCI. El [texto de diseño anterior](../../referencias/oficial/DISEÑO.md) también corresponde a esa etapa.

Las bibliotecas provienen del [catálogo público de Excalidraw](https://libraries.excalidraw.com/) y su [repositorio](https://github.com/excalidraw/excalidraw-libraries). Sus autores, enlaces, licencia y huellas se registran en [bibliotecas/FUENTES.json](bibliotecas/FUENTES.json).
