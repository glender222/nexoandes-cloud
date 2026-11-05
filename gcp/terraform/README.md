# GCP con Terraform — NexoAndes V2

Acceso y despliegue probados el 04/11/2026. Ver [CONTINUIDAD.md](../../integracion/CONTINUIDAD.md) y el [diseño V2](../../diagramas/excalidraw/DISENO_V2.md).

El módulo administra VPC, subred, firewalls, bucket privado/versionado, VM e2-micro y disco estándar de datos independiente. SSH requiere `admin_cidrs` explícitos y clave pública; la clave privada permanece en `integracion/privado/` o en el gateway de administración.

La VM permanece administrada al apagar: `desired_status=TERMINATED`, con disco de 20 GB conservado y arranque de 10 GB. VM, disco y bucket tienen `prevent_destroy`. El controlador también rechaza su eliminación. El estado de encendido de infraestructura no acredita por sí solo réplica ni failover.

El bootstrap usa `metadata["startup-script"]` para permitir actualizaciones de metadata sin reemplazar la VM. El 04/11 se migró la representación local de la misma instancia mediante respaldo y reimportación del mismo ID, sin recrearla. La configuración sensible de IPsec y PostgreSQL se entrega por canales administrativos y queda fuera de user-data y Terraform.

Para arrancar la demostración completa: `./nexoandes continuidad`. Para validar sin recursos reales: `./scripts/verificar-terraform.sh` (incluye pruebas mock del ciclo detener/conservar).
