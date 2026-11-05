# Comprobación de acceso y cambio de cuenta — 22/10/2026

## Resultado

Autenticación directa del agente confirmada mediante `aws/infraestructura/academy-aws sts get-caller-identity`. Cuenta activa: `849533029543`, rol asumido `voclabs`, región de trabajo del lector: `us-east-1`. El fallo de DNS anterior ya no se reprodujo (INC-010 resuelta en esta sesión).

La infraestructura histórica se documentó en la cuenta `669186512136`. No se verificó esa cuenta; no se concluye que sus recursos hayan sido eliminados.

## Recursos consultados

Se consultaron ambas regiones permitidas por el README del laboratorio, sin filtros de nombre para evitar excluir recursos renombrados.

| Consulta | us-east-1 | us-west-2 |
|---|---|---|
| VPC | Una VPC predeterminada, `172.31.0.0/16` | Una VPC predeterminada, `172.31.0.0/16` |
| EC2 no terminadas | 0 | 0 |
| Balanceadores ELBv2 | 0 | 0 |
| Auto Scaling Groups | 0 | 0 |
| NAT Gateways | 0 | 0 |
| Virtual Private Gateways | 0 | 0 |

S3: `list-buckets` devolvió una lista vacía. Todas estas consultas respondieron correctamente; no se interpretaron errores de permisos como listas vacías. Este inventario cubre los componentes consultados, no todos los servicios de AWS.

Los JSON de esta carpeta guardan los resultados; `consultas.json` registra los argumentos de cada consulta y `consultado_utc.txt` su fecha. Se conservaron las evidencias históricas de `../inventario-actual/`.

## Comprobación del perfil anterior

Se ejecutó además la siguiente consulta sin las credenciales exportadas en el entorno:

```bash
env -u AWS_ACCESS_KEY_ID -u AWS_SECRET_ACCESS_KEY -u AWS_SESSION_TOKEN \
  aws sts get-caller-identity --profile academy --region us-east-1 \
  --query '{Account:Account,Arn:Arn}' --output json \
  --cli-connect-timeout 10 --cli-read-timeout 20
```

Resultado: `ExpiredToken`. El perfil `academy` no proporciona acceso vigente; ese fallo tampoco confirma su cuenta asociada (INC-001).

## Opciones para continuar

1. **Recuperar el entorno anterior:** localizar en AWS Academy/Vocareum el Learner Lab de la cuenta `669186512136`, iniciar su sesión y obtener sus credenciales vigentes. Volver a comprobar STS y, si coincide la cuenta, inventariar antes de reactivar o publicar. No se pueden derivar credenciales nuevas de las caducadas ni cambiar de cuenta editando el ID del archivo.
2. **Continuar con la cuenta actual:** tratarla como un despliegue nuevo. Preparar configuración independiente, conservar IDs y evidencias históricos, completar la automatización y revisar costos antes de crear infraestructura. Datos de PostgreSQL de la cuenta anterior requerirían un respaldo accesible; no se encontraron copias en S3 de la cuenta actual.

## Dependencias locales de la cuenta anterior

- `aws/infraestructura/publicar-portal.sh` exige explícitamente `669186512136`; su validación debe mantenerse hasta definir la cuenta de destino.
- `aws/infraestructura/infra-params.env` contiene IDs y ARN históricos.
- `aws/infraestructura/inventario-lectura.sh` presupone la VPC `AWsAcademy-VPC`, un bucket histórico y la carpeta de salida `inventario-actual`; no se ejecutó para evitar mezclar cuentas o sobrescribir evidencias.
- Los scripts de creación requieren revisión antes de reutilizarlos: cambiar únicamente el número de cuenta no reconstruye la infraestructura.

No se crearon, actualizaron, publicaron ni eliminaron recursos AWS durante esta comprobación.
