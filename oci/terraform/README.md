# OCI con Terraform

Consulta la [guía común](../../infraestructura/README.md) para configurar tenancy, región home, compartment, dominio de disponibilidad e imagen Ubuntu ARM64. La nube empieza deshabilitada hasta preparar OCI CLI y el perfil API privado.

El módulo prepara VCN, reglas, VM A1 2 OCPU/12 GB con 50 GB de arranque y Object Storage. Apagar detiene la VM sin borrarla. Solo se crea Bastion cuando se configuran las redes de cliente autorizadas. No hay SSH público abierto por defecto, DRG ni IP reservada.

El host está preparado para strongSwan y una futura réplica: la VPN y PostgreSQL en streaming no se han configurado ni probado. Verifica consumo agregado Always Free antes de desplegar. Las validaciones y pruebas mock no acreditan capacidad disponible ni recursos reales.
