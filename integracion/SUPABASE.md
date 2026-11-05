# Supabase autohospedado en NexoAndes

## Estado real del 04/11/2026

**Implementado, arrancado y probado en AWS Academy**, cuenta `849533029543`, `us-east-1`. Supabase no depende de un proyecto Supabase Cloud ni de su plugin. Código open source fijado a `self-hosted/v0.8.3`, commit y huellas en [supabase/ORIGEN.json](supabase/ORIGEN.json).

- Instancia `nexoandes-supabase`, `i-0ceea48d268d2cb83`, t3.medium, 2 vCPU/4 GiB, subred privada `app_b`, sin IP pública.
- Disco de datos independiente, cifrado, gp3 de 40 GB. Instancia y disco protegidos contra destrucción en Terraform. `apagar` detiene la VM y conserva sus datos.
- Seis servicios saludables: PostgreSQL 17, Auth, PostgREST, postgres-meta, Studio y gateway Envoy. Storage, Realtime, Functions y Analytics no se habilitaron en esta primera instalación.
- PostgreSQL 15 principal de NexoAndes continúa separado. Supabase tiene su propia base para identidad; la réplica PostgreSQL 15 de GCP no incluye estos datos.
- API Auth/REST por HTTPS del ALB. HTTP rechaza API/credenciales y redirige la página de acceso a HTTPS. Studio se publica con credenciales administrativas por HTTPS 8443; también conserva el acceso por túnel SSM.

**Rol acordado para el proyecto académico:** Supabase se presenta como nuestro servicio SaaS académico de autenticación y backend, consumido por el portal mediante HTTPS. Esta decisión de alcance no cambia la clasificación técnica de la plataforma ni demuestra por sí sola el cumplimiento de un criterio SaaS de la rúbrica.

Supabase es una plataforma backend (BaaS/PaaS). Esta edición corre sobre nuestra IaaS; la aplicación NexoAndes incorpora login y un endpoint de identidad protegido. Pedidos, inventario y un producto SaaS comercial completo permanecen pendientes. No sustituye AWS IAM ni Active Directory.

## Studio externo — 04/11/2026 23:33 (America/Lima)

Publicado por solicitud del usuario en **https://nexoandes-alb-409538740.us-east-1.elb.amazonaws.com:8443/**. El navegador solicita el usuario y la contraseña del dashboard antes de cargar Studio. Son credenciales administrativas distintas de la cuenta de demostración del portal. El usuario y la contraseña permanecen en `integracion/privado/supabase/acceso-administracion.json`, con permisos 600 y ahora también el campo `url_externa`. No se copian a evidencias, Terraform ni al chat.

Ruta: Internet → ALB HTTPS 8443 → Envoy 8000 privado → Studio. Se reutiliza el certificado académico autofirmado y el target group existente. PostgreSQL, postgres-meta y la VM siguen sin exposición directa; `/pg`, `/pg/*`, `/mcp*` y `/api/mcp*` se bloquean en la entrada de Studio. Auth/REST siguen usando sus propias claves/tokens; el puerto 443 y el login del portal se conservan.

Prueba externa con verificación de firma y nombre TLS: sin credenciales 401, contraseña incorrecta 401, API Studio sin credenciales 401, panel autenticado 200, rutas meta/MCP 403. [Evidencia HTTP](evidencias/20261104/supabase/studio-externo.json), [navegador real](evidencias/20261104/supabase/studio-navegador.json), [publicación Terraform](evidencias/20261104/supabase/studio-publicacion.json). El certificado no tiene confianza pública: el navegador muestra advertencia; no se presenta como TLS de producción.

Terraform: `supabase_studio_external=true` en las variables privadas AWS, ya habilitado. `./nexoandes encender --nube aws` conserva la entrada; `./nexoandes apagar --nube aws` retira listeners temporales y detiene Supabase conservando sus datos. Para retirar solo la entrada externa, establecer `supabase_studio_external=false` y reconciliar AWS. Las pruebas mock comprueban que Studio no se publica por defecto ni sin certificado.

## Accesos

- [Login del portal](https://nexoandes-alb-409538740.us-east-1.elb.amazonaws.com/acceso/).
- [API de salud](https://nexoandes-alb-409538740.us-east-1.elb.amazonaws.com/auth/v1/health).
- [Studio externo con credenciales](https://nexoandes-alb-409538740.us-east-1.elb.amazonaws.com:8443/).
- Acceso alternativo por SSM en `http://127.0.0.1:8800` mientras el túnel esté activo. Para abrir otro túnel desde la raíz:

```bash
python3 integracion/abrir_supabase_studio.py
```

La cuenta de demostración está en `integracion/privado/supabase/acceso-demo.json`; el acceso administrativo está en `acceso-administracion.json` de esa misma carpeta privada, ambos con permisos 600. No copiar contraseñas, tokens o claves secretas al informe ni a capturas. El autoregistro está deshabilitado; la cuenta de prueba fue creada administrativamente con correo `.invalid`. No se configuró envío de correo/SMS.

El plugin CLI oficial Session Manager está instalado localmente en `infraestructura/privado/bin/session-manager-plugin`, sin modificar los paquetes del sistema. El túnel requiere credenciales AWS vigentes y la instancia activa; termina al cerrar su terminal o sesión. Si faltara el binario en otro equipo, seguir la [instalación oficial AWS](https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-debian-and-ubuntu.html).

**TLS académico:** certificado autofirmado de 30 días. El navegador puede mostrar advertencia de confianza; no es un certificado público. Las pruebas de API validaron nombre y firma con el certificado local, sin `-k`. La prueba de navegador utilizó una excepción limitada al pin SPKI de ese certificado.

## Reproducir y cerrar

```bash
# Con Learner Lab activo y credenciales renovadas cuando caduquen:
./nexoandes supabase

# Terminar la sesión conservando datos:
./nexoandes apagar
```

El entorno actual ya tiene PyYAML 6.0.2. Para aislar esa dependencia en otro entorno del proyecto, crear un venv privado con `python3 -m venv --system-site-packages integracion/privado/supabase/venv`, instalar `requirements.txt` con el Python de ese venv y ejecutar `integracion/arrancar_supabase.py` con ese mismo intérprete. Se conservan los requisitos previos del proyecto: AWS/Azure CLI y acceso Google Auth configurados.

El comando de Supabase valida identidad, publica un bootstrap web sin secretos administrativos, aplica Terraform AWS protegido, reconcilia TLS/URLs, configura la pila, prueba Auth y genera/copia su respaldo. No arranca cómputo Azure ni GCP. Para el ciclo multicloud completo sigue disponible `./nexoandes continuidad`, que también reconcilia Supabase si está habilitado.

El bootstrap de nuevas web del ASG descarga un artefacto privado S3 comprobado por SHA256. Solo incorpora la clave publicable; una validación Terraform rechaza claves `sb_secret`. El reemplazo real de una web instaló Auth automáticamente, sin intervención SSM para instalarlo.

## Pruebas realizadas

| Prueba | Resultado | Evidencia |
|---|---|---|
| Salud y login válido | HTTP 200, identidad confirmada por Auth | [pruebas-auth.json](evidencias/20261104/supabase/pruebas-auth.json) |
| Contraseña incorrecta | HTTP 400 | Mismo archivo |
| API privada sin token / token inventado | HTTP 401 / 401 | Mismo archivo |
| API privada con token válido | HTTP 200, identidad coincide | Mismo archivo |
| Logout | HTTP 204; token previo rechazado con 401 en el ensayo | Mismo archivo |
| HTTP en API y autoregistro | HTTP 403 y 422, respectivamente | Mismo archivo |
| Navegador escritorio/móvil | Login, acceso privado y logout correctos; sin desbordamiento móvil | [navegador.json](evidencias/20261104/supabase/navegador.json) |
| Stop/start Supabase | Misma VM y disco; usuario/checksum conservados; servicios recuperados sin reinstalar | [persistencia-reinicio.json](evidencias/20261104/supabase/persistencia-reinicio.json) |
| Reposición de web ASG | Reemplazo en 197,1 s con login y rechazo sin token instalados automáticamente | [arranque-web-asg.json](evidencias/20261104/supabase/arranque-web-asg.json) |
| Panel privado | Sin credenciales 401; con credenciales 200 a través del túnel | [studio-privado.json](evidencias/20261104/supabase/studio-privado.json) |

Los tokens de acceso duran cinco minutos y permanecen solo en memoria del navegador. El backend consulta Supabase Auth para validar la identidad; no confía en datos editables enviados por el cliente. El endpoint de demostración muestra únicamente la identidad propia y no implementa operaciones comerciales.

## Respaldos y recuperación

Timer de la VM `nexoandes-supabase-backup.timer`: cada hora, mientras esté encendida. Genera dumps de las bases y roles más configuración, claves y parámetros necesarios, en un archivo privado con permisos restrictivos. S3 cifra los objetos y tiene retención configurada de 14 días para el prefijo Supabase; la retención no equivale a inmutabilidad.

Para generar una copia y verificarla también en Azure/GCP:

```bash
python3 integracion/respaldos.py --tipo supabase --generar
```

La copia multicloud la ejecuta el equipo local por HTTPS autenticado; no es una automatización autónoma entre proveedores. El timer local anterior sigue deshabilitado por la pausa solicitada. No se necesita encender la VM GCP para subir objetos a Cloud Storage.

Las tres copias descargadas coincidieron en SHA256: [respaldos.json](evidencias/20261104/supabase/respaldos.json). Se restauró selectivamente `auth.users` en una BD temporal y coincidieron cantidad y checksum de identidades: [restauracion-auth.json](evidencias/20261104/supabase/restauracion-auth.json). **No se ha probado una restauración integral de toda la pila ni failover de Supabase a otra nube.**

## Límites y alcance

- Instalación académica de una sola VM; CPU T3 Standard y memoria medidas con carga pequeña, sin capacidad de producción demostrada.
- AWS Academy depende de sesiones, credenciales y presupuesto. Una caída completa de AWS afecta nuevos inicios de sesión aunque GCP conserve datos del sistema anterior.
- No se incorporó RLS de tablas comerciales porque todavía no existen tablas de aplicación expuestas en `public`. Antes de incorporar datos de negocio se diseñarán autorización y RLS específicas.
- El trayecto público usa TLS académico; los trayectos ALB/backend/gateway internos usan HTTP dentro de la VPC. No se afirma cifrado de tránsito completo de producción.
- El cómputo queda activo por solicitud del usuario y consume crédito. Al apagar persiste almacenamiento que también puede consumirlo; saldo real y costo total del laboratorio no verificados.
- Incidencias de bootstrap y reconexión corregidas: INC-026/027/028, en [REGISTRO.md](../incidencias/REGISTRO.md). Las inicializaciones fallidas se conservaron bajo `.fallos` en el disco, sin tocar PostgreSQL principal. Los paquetes temporales con secretos de bootstrap se retiraron de S3; los respaldos privados permanecen.

Fuentes técnicas: [Supabase Docker](https://supabase.com/docs/guides/self-hosting/docker), [Auth](https://supabase.com/docs/guides/auth), [modelo PaaS](https://supabase.com/docs/guides/integrations/supabase-for-platforms), [EC2](https://docs.aws.amazon.com/ec2/latest/instancetypes/gp.html).

Validación final: 15 pruebas unitarias, 9 pruebas mock Terraform y plan AWS sin cambios. [Validación local](evidencias/20261104/supabase/validacion-local.json). El [mapa editable y exportaciones](../diagramas/excalidraw/README.md) ya incluyen Supabase.

## Alcance acordado — 05/11/2026

El usuario indicó no continuar con el ensayo de restauración integral de Supabase. Se retira del trabajo activo; se conservan las copias verificadas y la prueba selectiva de auth.users como evidencia existente. No se declara recuperación integral probada. No se hicieron cambios cloud por esta decisión.
