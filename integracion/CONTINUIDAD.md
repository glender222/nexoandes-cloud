# Operar y comprobar NexoAndes V2

El diseño está en [Excalidraw](../diagramas/excalidraw/nexoandes-multicloud.excalidraw) y [DISENO_V2.md](../diagramas/excalidraw/DISENO_V2.md). El estado y las mediciones del 04/11/2026 se consultan en las [evidencias](evidencias/20261104/) y en el [informe de estado](../diagramas/excalidraw/ESTADO_2026-11-04.md).

## Reencender la demostración

1. Iniciar Learner Lab y renovar las tres credenciales en `aws/privado/academy-session.env` cuando caduquen. No pegarlas en documentación ni chat.
2. Desde la raíz, ejecutar:

```bash
./nexoandes continuidad
```

El flujo aplica planes protegidos, reconcilia las IP públicas de ambos extremos, prepara la clave SSH del gateway, configura IPsec y prepara réplica y sondas. No crea usuarios IAM ni cambia las SCP. GCP conserva su VM y disco al apagar; el gateway AWS y las web son temporales.

La administración automatizada de GCP usa SSH desde el gateway AWS, autenticado con clave propia y restringido por firewall a ese origen. La clave privada permanece en el gateway; la PSK IPsec y las contraseñas locales están en `integracion/privado/`. Las IP de salida del equipo cambiaron durante las pruebas y no se abrió SSH a todo Internet. El acceso administrativo independiente mediante consola/IAP no forma parte de las pruebas completadas.

El controlador exige una IP GCP no vacía y una CHILD_SA IPsec instalada antes de preparar la réplica (INC-023). La verificación GCP del arranque se realiza desde el gateway AWS y registra aparte el resultado local: durante este ciclo FortiGuard bloqueó la nueva IP como Unrated (INC-024). Para acceso desde esa red se necesita la revisión de su política; no se cambió ni sorteó el filtro local.

El ALB y la IP pública de GCP pueden cambiar al reencender. Consultar los outputs vigentes; no reutilizar URLs de un ensayo anterior como garantía de disponibilidad actual.

El flujo también configura HTTPS académico en el ALB y verifica nombre/certificado con `curl --cacert`, sin usar `-k`. El certificado es autofirmado, dura 30 días y no tiene confianza pública; el navegador del usuario mostrará advertencia. HTTP permanece disponible para las pruebas. El portal alternativo GCP usa HTTP; no se presenta como cifrado web completo de producción.

## Operación y pruebas

```bash
./nexoandes comprobar
python3 integracion/inventario.py --salida infraestructura/evidencias/inventario-actual.json
python3 integracion/respaldos.py --generar
python3 integracion/prueba_trafico.py
python3 integracion/prueba_fallo_web.py
python3 integracion/prueba_failover.py --ejecutar
```

Las tres últimas órdenes generan carga o fallas controladas; ejecutar una por vez. La prueba de tráfico tiene duración acotada y retira su carga. El umbral de 30 solicitudes por destino/minuto es de demostración, no dimensionamiento para 5000 usuarios. El crecimiento se observa en el ASG; el retorno a dos instancias se solicita manualmente y se identifica como tal.

`/health` consulta PostgreSQL y devuelve únicamente el rol de recuperación y el último identificador de una tabla sintética. El portal original sigue siendo informativo. Las instancias web nuevas necesitan reconciliación con `preparar_continuidad.py`; el arranque de la demostración realiza esa preparación. El reemplazo del servidor web se evalúa sobre el portal estático, y la continuidad de datos se evalúa por separado sobre la sonda.

La conmutación de BD se solicita manualmente: esperar réplica, detener el timer de respaldo, aislar el primario AWS y bloquear su reinicio accidental, promover GCP y cambiar la conexión de las sondas. El ensayo comprueba escritura en GCP y retorno a AWS mediante reseed físico; conserva la copia anterior de cada directorio de datos. No se inicia automáticamente un primario antiguo tras un fallo del ensayo. Si el proceso se interrumpe, leer `failover.json` y comprobar los roles antes de reiniciar nada.

El ensayo de acceso alternativo detiene procesos web y BD de AWS y consulta el portal GCP por su URL independiente. No interrumpe realmente el proveedor AWS ni prueba la pérdida del plano de administración; no demuestra failover DNS automático.

## Respaldos automáticos

El primario AWS tiene un timer de `pg_dump` horario a S3 mientras está activo. Para copiar el último dump a Azure y GCP, y descargarlo para comparar SHA256:

```bash
python3 integracion/instalar_respaldo_automatico.py
systemctl --user status nexoandes-respaldos.timer
```

**Pausa solicitada el 04/11/2026:** el timer local quedó detenido y deshabilitado para dejar el proyecto en espera. Para reactivarlo en la próxima sesión, ejecutar `python3 integracion/instalar_respaldo_automatico.py`; el comando de continuidad por sí solo no lo habilita.

El timer del equipo se ejecuta cada hora con retraso aleatorio de hasta cinco minutos. Necesita equipo/sesión disponibles, red y credenciales vigentes. No enciende nubes ni genera dumps en una BD detenida. No es una automatización autónoma alojada entre proveedores. Para retirarlo:

```bash
systemctl --user disable --now nexoandes-respaldos.timer
```

La retención y el versionado no equivalen a inmutabilidad. Los datos y claves de cuenta no se publican en las evidencias. La restauración en una base temporal se acredita con SQL y se distingue de la mera igualdad de hashes.

## Terminar la sesión

```bash
./nexoandes apagar
python3 integracion/inventario.py --salida infraestructura/evidencias/inventario-final.json
```

El apagado retira ALB/ASG/NAT/gateway temporal AWS, detiene PostgreSQL y detiene la misma VM GCP conservando sus discos. Azure conserva sus respaldos y red. Almacenamiento y otras cargas de las cuentas pueden consumir crédito. No modifica las VMs de examen o Antigravity ajenas a NexoAndes. La réplica apagada no recibe cambios; las pruebas de disponibilidad corresponden a sesiones activas del laboratorio.

## Validación local

```bash
./scripts/verificar-terraform.sh
python3 -m py_compile integracion/*.py
```

Las pruebas mock comprueban los ciclos y protecciones sin crear recursos. Las evidencias reales conservan fecha, comando, resultado y límites del ensayo. Las capturas del usuario y el número definitivo de equipo siguen siendo trabajo de preparación de los entregables.
