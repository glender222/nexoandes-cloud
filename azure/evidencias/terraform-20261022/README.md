# Terraform Azure — comprobación real del 22/10/2026

Suscripción Azure for Students `1db87b28-407f-41d3-b532-41942343157c`, tenant `cfbd88b4-94bc-4fba-98bd-64d0726394a3`, región `northcentralus` admitida por la política de la suscripción.

## Resultado

- Identidad y política: `identidad.json`, `regiones-permitidas.json`.
- Network y Storage registrados: `proveedor-network.json`, `proveedor-storage.json`.
- Plan y apply reales: seis altas Terraform, sin bajas. Se crearon grupo `nexoandes-lab`, VNet `nexoandes-vnet`, GatewaySubnet, Storage Account `nxa1db87b28407f`, contenedor privado `postgresql` y política de retención. `recursos-encendido.json` enumera recursos superiores; subred, contenedor y política son recursos hijos.
- Se copió desde S3 el dump `postgresql/20261022T205410Z.dump`, de 1868 bytes, a Blob. Se descargó de nuevo y ambos SHA256 coincidieron: `copia-respaldo-verificada.json`.
- `./nexoandes apagar` terminó en ambas nubes. Azure conservó sus seis recursos; no había gateway ni cómputo habilitado para retirar. Output `encendido=false`: `outputs-apagado-final.json`. Recursos conservados: `recursos-apagado-final.json`. Resultado del controlador: `operacion-apagado-final.json`.
- Después del apagado se descargó nuevamente el Blob y coincidió con el SHA256 original de S3: `respaldo-apagado-final.json`. Fecha de comprobación: `verificado-final-utc.txt`.
- Un nuevo `./nexoandes plan apagar` consultó los recursos reales y terminó sin cambios: `plan-apagar-sin-cambios.json`.

La copia fue manual mediante CLI; no se han automatizado envíos, configurado VPN ni restaurado una base de datos en Azure. VPN Gateway y Log Analytics están deshabilitados. Almacenamiento retenido y operaciones pueden consumir crédito; el output apagado no significa eliminar datos ni gasto cero.

No se incluyen claves, tokens, dumps ni estados Terraform en esta carpeta. El dump queda en el almacenamiento privado de cada nube y los archivos temporales de prueba se eliminaron.
