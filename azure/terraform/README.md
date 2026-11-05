# Azure con Terraform

Consulta la [guía común](../../infraestructura/README.md) para configurar suscripción, tenant y acceso CLI. La configuración actual ya habilita Azure y el despliegue real del 22/10/2026 está registrado en [avances](../AVANCES.md); el archivo de ejemplo empieza deshabilitado hasta completar esos valores.

El módulo crea Resource Group, VNet y Blob privado. VPN Gateway y Log Analytics son opcionales y están deshabilitados inicialmente. Apagar conserva los respaldos y retira el gateway y su IP si se habilitaron. No existe aún envío automático de respaldos desde AWS ni túnel configurado.

Las validaciones y pruebas mock se pueden ejecutar sin una cuenta Azure. No equivalen a un despliegue real.
