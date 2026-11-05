# AWS con Terraform

Usa el [control común](../../infraestructura/README.md), no los scripts históricos de creación.

```bash
./nexoandes comprobar --nube aws
./nexoandes plan encender --nube aws
./nexoandes encender --nube aws
./nexoandes apagar --nube aws
```

Ejecutar desde la raíz. Cuenta y región se validan contra `infraestructura/privado/config.json`. Estado local separado por cuenta/región; credenciales temporales en `aws/privado/academy-session.env`. El apagado conserva la DB, el volumen de datos y S3; no es un borrado total ni gasto cero. HTTPS necesita un certificado ACM configurado. Las validaciones y pruebas mock no acreditan despliegue real.
