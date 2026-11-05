# Terraform AWS — comprobación real del 22/10/2026

Cuenta `849533029543`, región `us-east-1`. Estas pruebas corresponden al despliegue nuevo; las evidencias anteriores de otra cuenta se conservan por separado.

## Resultado

1. Encendido real: portal HTTP 200, dos targets healthy y PostgreSQL activo. Ver `http-antes.txt`, `targets-antes.json` y `prueba-db-inicial.json`.
2. Respaldo real a S3 y restauración en una base temporal: se recuperó el marcador `terraform-20261022`; después se eliminó esa base temporal. Ver `prueba-restauracion.json`.
3. Primer apagado: DB detenida, disco persistente conservado y ALB/ASG/NAT retirados. Ver archivos `*-apagado-1.json`.
4. Reencendido: misma EC2 DB y mismo volumen; PostgreSQL activo y marcador conservado. Portal nuevamente HTTP 200. Ver `outputs-reencendido.json`, `http-reencendido.txt` y `prueba-db-reencendido.json`.
5. Copia del dump S3 a Azure Blob y descarga con SHA256 idéntico: [prueba Azure](../../../azure/evidencias/terraform-20261022/copia-respaldo-verificada.json). Fue una copia manual mediante CLI.
6. Apagado conjunto real `./nexoandes apagar`, completado en AWS y Azure. Estado final AWS: solo la DB `i-01ae7353f82b8daa5` detenida; mismo disco cifrado `vol-0641bf3d4c25b6b34` de 20 GB; sin ALB, ASG, NAT activo ni EIP asignada. El dump sigue en S3. Ver archivos `*-apagado-final.json`, `operacion-apagado-final.json` y fecha `verificado-final-utc.txt`.

VPC conservada: `vpc-0ab83bf4a2b225c41`. Bucket: `nexoandes-backup-849533029543-us-east-1`. El apagado no borra los discos de la DB ni los respaldos; ese almacenamiento puede seguir generando consumo. La URL del ALB de las pruebas ya no está disponible mientras permanezca apagado y cambiará al reconstruirse.

Se volvió a ejecutar `./nexoandes plan apagar` después del apagado: cero cambios reales en AWS y Azure. Resumen: `plan-apagar-sin-cambios.json`.

## Repetir el ciclo

Con el Learner Lab iniciado y credenciales renovadas en el archivo privado:

```bash
./nexoandes comprobar
./nexoandes encender
./nexoandes estado
./nexoandes apagar
```

`estado` muestra el último estado guardado. Las pruebas de esta carpeta incluyen consultas directas a los servicios; no dependen solo de ese estado.

El timer horario de respaldo quedó habilitado y sobrevivió al reencendido; se probó su helper manualmente, sin esperar una ejecución horaria. No se probaron notificaciones de alarmas, VPN, réplica OCI ni escalado bajo carga en esta cuenta. HTTPS requiere configurar un certificado ACM actual.

`validacion-local.json` distingue validaciones y tests simulados de las pruebas anteriores. Los planes completos, estados y logs con datos sensibles permanecen en `infraestructura/privado/`; no se incluyen en el entregable.
