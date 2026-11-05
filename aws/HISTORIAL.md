> Archivo histórico trasladado a `aws/`. Los comandos y rutas que contiene describen sesiones anteriores y pueden apuntar a la ubicación antigua. Para trabajar ahora, comienza en [`README.md`](../README.md) y [`ACCESO.md`](ACCESO.md). No usar este historial como prueba de estado actual.

# DESARROLLO CLOUD COMPUTING — AWsAcademy

> **Audiencia:** agentes de IA, estudiantes y desarrolladores que retoman este proyecto.
> **Propósito:** documentar TODO lo ejecutado, herramientas CLI utilizadas, credenciales,
> errores encontrados, soluciones aplicadas, y cómo replicar el entorno desde cero.
> **Fecha del despliegue:** 17 Septiembre 2026
> **Cuenta AWS Academy / Vocareum:** `669186512136`
> **Rol:** `voclabs/user5367530=Glender_Vargas`
> **Región:** `us-east-1`

---

## ⚠️ LEE ESTO PRIMERO — CREDENCIALES TEMPORALES (TODO AGENTE DEBE SABERLO)

**Las credenciales de AWS Academy / Vocareum expiran cada ~30-45 minutos. NO son permanentes.**

Esto significa que **cada vez que un agente retome este proyecto**, incluso si la sesión anterior funcionaba perfectamente, lo primero que va a pasar es que `aws sts get-caller-identity` falle con:

- `ExpiredTokenException` — "The security token included in the request is expired"
- `InvalidClientTokenId` — "The security token included in the request is invalid"

### Cómo detectar que el token expiró

```bash
AWS_PROFILE=academy aws sts get-caller-identity
```

Si devuelve **cualquier error**, el token expiró. No intentes otro comando AWS. Ve directo a renovar.

### Cómo renovar el token (procedimiento exacto)

**Paso 1 — El humano debe intervenir:** Las credenciales se obtienen desde la terminal de **Vocareum** (no desde la laptop local). El agente NO PUEDE hacer esto solo. Debe pedirle al usuario que:

1. Vaya al panel de Vocareum (AWS Academy)
2. Si el lab está apagado → clic en **Start Lab**, esperar a que el círculo se ponga verde
3. Clic en **AWS Details**
4. En la terminal de Vocareum ejecute:
   ```bash
   aws configure export-credentials --format env
   ```
5. Copie las 3 variables y se las pase al agente:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_SESSION_TOKEN`

**Paso 2 — El agente debe configurarlas:**

```bash
# Opción A: escribirlas en ~/.aws/credentials (persiste entre comandos)
cat > ~/.aws/credentials << 'EOF'
[academy]
aws_access_key_id = <PEGAR_AQUÍ>
aws_secret_access_key = <PEGAR_AQUÍ>
aws_session_token = <PEGAR_AQUÍ>
EOF

# Opción B: exportarlas como variables de entorno (solo para esta shell)
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."
export AWS_DEFAULT_REGION=us-east-1
export AWS_PROFILE=academy
```

**Paso 3 — Verificar inmediatamente:**

```bash
AWS_PROFILE=academy aws sts get-caller-identity
# Debe devolver:
# {
#   "UserId": "AROAZXTU72UEBBGZRKENO:user5367530=Glender_Vargas",
#   "Account": "669186512136",
#   "Arn": "arn:aws:sts::669186512136:assumed-role/voclabs/user5367530=Glender_Vargas"
# }
```

### Por qué es importante

| Comportamiento | Causa |
|---|---|
| ❌ `aws ec2 describe-instances` falla con `ExpiredToken` | Token venció |
| ❌ `start-lab.sh` falla al primer comando | Token venció |
| ⚠️ El ALB no responde y pensás que es la infra | Token venció (no podés verificar) |
| ⚠️ Vocareum devuelve el mismo token una y otra vez | Bug conocido — hacer **Stop Lab → Start Lab** |

**Regla de oro:** si un comando AWS falla, **asumí primero que el token expiró** antes de asumir que la infraestructura está rota. El 90% de los errores en este proyecto son por token vencido, no por infraestructura rota.

---

## 1. INVENTARIO DEL ENTORNO DE DESARROLLO

### 1.1 Hardware y SO

| Componente | Detalle |
|---|---|
| Equipo | Laptop |
| Sistema operativo | Debian 13 (trixie) |
| Kernel | `6.12.107+deb13-amd64` |
| Sistema de archivos | **RAÍZ READ-ONLY** (`/` montado `ro`) — solo el workspace (`/home/glender/Proyectos/AWsacademy`) es `rw` |
| Workspace | `/home/glender/Proyectos/AWsacademy` |

> ⚠️ **HALLAZGO CRÍTICO:** El filesystem raíz está montado como `ro,nosuid,nodev,relatime`.  
> Cualquier herramienta que intente **escribir fuera del workspace** fallará con `OSError: [Errno 30] Read-only file system`.  
> Esto afecta a `az` (Azure CLI) que intenta escribir `~/.azure/az.sess`.

### 1.2 Herramientas CLI instaladas

| Herramienta | Versión | Instalada vía | Estado |
|---|---|---|---|
| **AWS CLI** | `aws-cli/2.36.47 Python/3.14.6` | Paquete oficial (exe/x86_64.debian.13) | ✅ Funcional |
| **Azure CLI** | `2.x` (instalado) | `pipx` en `~/.local/share/pipx/venvs/azure-cli` | ❌ ROTO — `OSError: [Errno 30] Read-only file system` al escribir `~/.azure/az.sess` |
| **OCI CLI** | — | — | ❌ NO INSTALADO |
| **uv** | `0.12.5` | `pipx` | ✅ Funcional |
| **Python** | `3.13.5` | Sistema | ✅ Funcional |
| **psql** | `17.11 (Debian 17.11-0+deb13u1)` | `apt` | ✅ Funcional |
| **jq** | `1.7` | `apt` | ✅ Funcional |
| **Docker** | `29.8.0, build 88096ef` | `apt` | ✅ Funcional |
| **SSH** | OpenSSH (sistema) | Sistema | ✅ Funcional |
| **Tailscale** | — | — | ⚠️ Instalado EN LAS EC2, NO en la laptop local |

### 1.3 Perfiles y configuración AWS

**Archivo `~/.aws/config`:**
```ini
[profile academy]
region = us-east-1
output = json
```

**Archivo `~/.aws/credentials`:**
```ini
[academy]
aws_access_key_id = <TEMPORAL — VOCAREUM>
aws_secret_access_key = <TEMPORAL — VOCAREUM>
aws_session_token = <TEMPORAL — VOCAREUM>
```

> Las credenciales son **temporales** (~30-45 min). Hay que renovarlas constantemente desde Vocareum.

---

## 2. FLUJO DE CREDENCIALES AWS ACADEMY / VOCAREUM

### 2.1 Cómo obtener credenciales

1. Ir al panel de **Vocareum** (AWS Academy)
2. Si el lab está apagado → **Start Lab** y esperar que el círculo se ponga verde
3. Clic en **AWS Details** → muestra credenciales
4. En la terminal de Vocareum ejecutar:
   ```bash
   aws configure export-credentials --format env
   ```
5. Copiar las 3 variables de entorno + `AWS_CREDENTIAL_EXPIRATION`
6. Pegarlas en `~/.aws/credentials` bajo el perfil `[academy]`:
   ```ini
   [academy]
   aws_access_key_id = ASIA...
   aws_secret_access_key = ...
   aws_session_token = IQoJ...
   ```
   O setearlas como variables de entorno directamente.

### 2.2 Verificar que funcionan

```bash
AWS_PROFILE=academy aws sts get-caller-identity
```

Respuesta esperada:
```json
{
  "UserId": "AROAZXTU72UEBBGZRKENO:user5367530=Glender_Vargas",
  "Account": "669186512136",
  "Arn": "arn:aws:sts::669186512136:assumed-role/voclabs/user5367530=Glender_Vargas"
}
```

### 2.3 Errores comunes con credenciales

| Error | Causa | Solución |
|---|---|---|
| `InvalidClientTokenId` | Token expirado o mal copiado | Renovar en Vocareum |
| `ExpiredToken` | La sesión venció (típicamente 30-45 min) | Renovar en Vocareum |
| `AccessDenied` con política `voc-cancel-cred` | El lab se reinició con políticas restrictivas | Esperar o reiniciar el lab de nuevo |
| Vocareum devuelve el mismo token una y otra vez | Bug conocido | **Stop Lab → Start Lab** para forzar nuevas credenciales |
| `aws login` no funciona | Academy no soporta `aws login` (sin consola AWS) | Usar solo credenciales temporales manuales |

---

## 3. AGENT TOOLKIT FOR AWS + MCP SERVER

### 3.1 Qué es

El **Agent Toolkit for AWS** (`aws agent-toolkit`) es una CLI que instala skills específicos de AWS y configura un **MCP Server** (`mcp-proxy-for-aws`) que actúa como puente entre agentes de IA (Claude Code, Codex, Gemini CLI, OpenCode) y la API MCP de AWS.

### 3.2 Instalación

```bash
# Requisito previo: perfil academy ya configurado y funcional
aws configure set region us-east-1 --profile academy

# Instalar el toolkit (configura skills + MCP server)
aws configure agent-toolkit --yes --region us-east-1 --profile academy
```

> **Nota importante:** `aws configure agent-toolkit` es un comando de 3 palabras (no es `aws agent-toolkit configure`).  
> Es parte de la funcionalidad `configure` del CLI, como `aws configure set` o `aws configure list`.

### 3.3 Resultado de la instalación

**Agentes detectados:**
| Agente | Ruta | Estado |
|---|---|---|
| Claude Code | `~/.claude/skills` | ✅ Detectado |
| Codex | `~/.agents/skills/` | ✅ Detectado |
| Gemini CLI | `~/.agents/skills/` | ✅ Detectado |
| OpenCode | `~/.agents/skills/` | ✅ Detectado |
| Cline | — | ❌ No encontrado |
| Cursor | — | ❌ No encontrado |

**Skills instalados (25):** `amazon-bedrock`, `aws-ai-ml`, `aws-auth`, `aws-billing-and-cost-management`, `aws-blocks`, `aws-cdk`, `aws-cloudformation`, `aws-compute`, `aws-containers`, `aws-database`, `aws-deployment`, `aws-iam`, `aws-messaging-and-streaming`, `aws-networking`, `aws-observability`, `aws-sdk-js-v3-usage`, `aws-sdk-python-usage`, `aws-sdk-swift-usage`, `aws-security`, `aws-serverless`, `aws-storage`, `launch-with-aws`, `quant-rules`, `quant-validation`, `signing-in-to-aws`

### 3.4 Corrección manual del MCP Server

**Problema:** el entry `aws-mcp` generado por el toolkit apunta al perfil `default` que no existe.  
**Síntoma:** `JSON-RPC error: -32602: Invalid request parameters("")`.

**Archivos modificados y su estructura final:**

| Archivo | Formato |
|---|---|
| `~/.claude.json` | `{ "mcpServers": { "aws-mcp": { "command": "uvx", "args": [...], "env": { "AWS_MCP_PROXY_PROFILES": "academy" } } } }` |
| `~/.gemini/settings.json` | Mismo esquema bajo la clave `mcpServers` |
| `~/.config/opencode/opencode.json` | Mismo esquema bajo la clave `mcp` |

**Corrección aplicada:** se agregó el bloque `"env": { "AWS_MCP_PROXY_PROFILES": "academy" }` a cada entry.

> Se usó `AWS_MCP_PROXY_PROFILES` (no `AWS_PROFILE`) porque habilita cambio cross-account a futuro.

### 3.5 Verificación

```bash
aws agent-toolkit list-available-skills --region us-east-1 --profile academy
```

Devuelve el catálogo completo de skills remotos con `name`, `description`, `skillVersion` y `categories`.

---

## 4. ARQUITECTURA CLOUD DESPLEGADA EN AWS

### 4.1 Diagrama de arquitectura

```
                         INTERNET
                             │
                             ▼
                   ┌─────────────────┐
                   │  LOAD BALANCER  │
                   │  ALB (público)  │ ✅ healthy
                   │  HTTP 80        │
                   └────────┬────────┘
                            │
               AWS VPC 10.10.0.0/16
                            │
          ┌─────────────────┴─────────────────┐
          │                                   │
   AZ us-east-1a                       AZ us-east-1b
          │                                   │
    Public subnet A                     Public subnet B
     10.10.1.0/24                       10.10.2.0/24
          │                                   │
          │            ┌──────────┐           │
          └────────────│ NAT GW   │───────────┘
                       └────┬─────┘
                            │
    Private App A                   Private App B
    10.10.11.0/24                   10.10.12.0/24
          │                                   │
       EC2 APP01 ✅                      EC2 APP02 ✅
    10.10.11.119                       10.10.12.82
    Apache httpd                       Apache httpd
          │                                   │
          └───────────────┬───────────────────┘
                          │
                  Database subnet
                   10.10.20.0/24
                          │
                   EC2 PostgreSQL ✅
                   10.10.20.125
                   Puerto 5432
```

### 4.2 FASE 1 — VPC y Redes

**Script:** `deploy-infra.sh`  
**Comandos clave usados:**

```bash
# VPC
aws ec2 create-vpc --cidr-block 10.10.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=AWsAcademy-VPC}]'

# Habilitar DNS
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames '{"Value":true}'
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support '{"Value":true}'

# Internet Gateway
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=AWsAcademy-IGW}]'
aws ec2 attach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID

# NAT Gateway (requiere Elastic IP)
aws ec2 allocate-address --domain vpc
aws ec2 create-nat-gateway --subnet-id $SUBNET_PUB_A --allocation-id $EIP_ALLOC
aws ec2 wait nat-gateway-available --nat-gateway-ids $NAT_GW_ID

# Subnets (5)
aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.10.X.0/24 \
  --availability-zone us-east-1a --tag-specifications '...'

# Auto-assign public IP (solo públicas)
aws ec2 modify-subnet-attribute --subnet-id $SUBNET_PUB_A --map-public-ip-on-launch

# Route tables
aws ec2 create-route-table --vpc-id $VPC_ID --tag-specifications '...'
aws ec2 create-route --route-table-id $RTB_PUBLIC --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
aws ec2 create-route --route-table-id $RTB_PRIVATE --destination-cidr-block 0.0.0.0/0 --nat-gateway-id $NAT_GW_ID
aws ec2 associate-route-table --route-table-id $RTB --subnet-id $SUBNET

# Security Groups (3 capas)
aws ec2 create-security-group --group-name AWsAcademy-ALB-SG --vpc-id $VPC_ID
aws ec2 authorize-security-group-ingress --group-id $SG_ALB --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_APP --protocol tcp --port 80 --source-group $SG_ALB
aws ec2 authorize-security-group-ingress --group-id $SG_DB --protocol tcp --port 5432 --source-group $SG_APP

# Key Pair
aws ec2 create-key-pair --key-name AWsAcademy-Key --query 'KeyMaterial' --output text > AWsAcademy-Key.pem
chmod 400 AWsAcademy-Key.pem
```

**Recursos creados:**

| Recurso | ID | Detalle |
|---|---|---|
| VPC | `vpc-02ce46dbb9aa3e25e` | `10.10.0.0/16`, DNS habilitado |
| IGW | `igw-08ca56f943a682da1` | Adjunto a la VPC |
| NAT GW | `nat-0cbe05db5bee351ac` | EIP `eipalloc-058d4af932b1c43cc` |
| Public-A | `subnet-0531e22c018004601` | `10.10.1.0/24`, `us-east-1a` |
| Public-B | `subnet-0d1771756ad8bbb5a` | `10.10.2.0/24`, `us-east-1b` |
| PrivateApp-A | `subnet-09855fbfb1cee5431` | `10.10.11.0/24`, `us-east-1a` |
| PrivateApp-B | `subnet-05b5cc3955fb40df9` | `10.10.12.0/24`, `us-east-1b` |
| PrivateDB | `subnet-0bbbde4bc4faebf5a` | `10.10.20.0/24`, `us-east-1a` |
| RTB-Public | `rtb-01d8ae31a09ee1ff2` | `0.0.0.0/0` → IGW |
| RTB-Private | `rtb-07a73075461d33dc8` | `0.0.0.0/0` → NAT GW |
| SG-ALB | `sg-0e8fa6cda3a29e39d` | HTTP:80 + HTTPS:443 desde `0.0.0.0/0` |
| SG-App | `sg-0ddb1f893793d43c2` | HTTP:80 desde SG-ALB, SSH:22 desde `0.0.0.0/0` |
| SG-DB | `sg-08782804aa36c65ff` | PostgreSQL:5432 desde SG-App |
| Key Pair | `AWsAcademy-Key` | Guardada en `AWsAcademy-Key.pem` |

### 4.3 FASE 2 — Servidores de Aplicación

**Script:** `deploy-ec2.sh`  
**Comandos clave:**

```bash
# Buscar AMI más reciente de Amazon Linux 2023
aws ec2 describe-images --owners amazon \
  --filters 'Name=name,Values=al2023-ami-2023*-x86_64' 'Name=state,Values=available' \
  --query 'sort_by(Images,&CreationDate)[-1].ImageId' --output text

# Launch Template con user-data (en Base64)
aws ec2 create-launch-template \
  --launch-template-name AWsAcademy-LT \
  --launch-template-data '{
    "ImageId": "ami-05dee78f58650ed2c",
    "InstanceType": "t3.micro",
    "KeyName": "AWsAcademy-Key",
    "SecurityGroupIds": ["sg-0ddb1f893793d43c2"],
    "IamInstanceProfile": {"Name": "LabInstanceProfile"},
    "UserData": "<BASE64>"
  }'

# Auto Scaling Group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name AWsAcademy-ASG \
  --launch-template "LaunchTemplateId=lt-03f9c1b47cfa22b8c" \
  --min-size 2 --max-size 4 --desired-capacity 2 \
  --vpc-zone-identifier "subnet-09855...,subnet-05b5c..." \
  --health-check-type ELB --health-check-grace-period 120
```

**⛔ Error encontrado:** `iam:CreateRole` → **AccessDenied**.  
**🔧 Solución:** se reutilizó el `LabInstanceProfile` (rol `LabRole`) que ya existía en la cuenta Academy.

**Instancias activas (último estado conocido):**

| Nombre | Instance ID | AZ | IP Privada | Software |
|---|---|---|---|---|
| APP01 | `i-04bc022b4ec444f5d` | `us-east-1a` | `10.10.11.119` | Apache httpd |
| APP02 | `i-011de71ed8ff7912a` | `us-east-1b` | `10.10.12.82` | Apache httpd |

> Las instancias originales (`i-00ced...` y `i-0affd...`) fueron terminadas al expirar el lab.  
> El ASG lanzó reemplazos automáticamente → **el Auto Scaling funciona correctamente.**

### 4.4 FASE 3 — Application Load Balancer

**Comandos clave:**

```bash
# Target Group
aws elbv2 create-target-group --name AWsAcademy-TG --protocol HTTP --port 80 \
  --vpc-id vpc-02ce46dbb9aa3e25e --health-check-path /

# ALB (internet-facing, en subnets públicas)
aws elbv2 create-load-balancer --name AWsAcademy-ALB \
  --subnets subnet-0531e22c018004601 subnet-0d1771756ad8bbb5a \
  --security-groups sg-0e8fa6cda3a29e39d

# Listener HTTP 80
aws elbv2 create-listener --load-balancer-arn $ALB_ARN \
  --protocol HTTP --port 80 \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN

# Registrar targets
aws elbv2 register-targets --target-group-arn $TG_ARN --targets Id=$INSTANCE_ID,Port=80

# Verificar salud
aws elbv2 describe-target-health --target-group-arn $TG_ARN
```

**⛔ Error encontrado:** tras reiniciar el lab, el **listener desapareció** del ALB.  
El ALB seguía `active` pero sin listener → sin tráfico → health check `unused` con razón `Target.NotInUse`.  
**🔧 Solución:** recrear el listener (1 comando). Inmediatamente ambas instancias pasaron a `healthy`.

**URL pública:** `http://AWsAcademy-ALB-1953310462.us-east-1.elb.amazonaws.com`

**Respuesta HTTP verificada:**
```html
<h1>APP01 - AWsAcademy</h1>
<p>ID: i-04bc022 | AZ: us-east-1a | IP: 10.10.11.119</p>
```

### 4.5 FASE 4 — Base de Datos

**⛔ Error encontrado:** `rds:CreateDBInstance` → **AccessDenied**.  
**🔧 Solución (Plan B):** PostgreSQL 15 instalado en EC2 en la subnet de base de datos.

**Script de instalación:** `db-user-data.sh`

**Comandos clave:**
```bash
# En la EC2 de base de datos:
yum install -y postgresql15-server
postgresql-setup --initdb
systemctl enable postgresql && systemctl start postgresql

# Configurar acceso desde las apps
echo "listen_addresses = '*'" >> /var/lib/pgsql/data/postgresql.conf
echo "host all all 10.10.0.0/16 md5" >> /var/lib/pgsql/data/pg_hba.conf
systemctl restart postgresql

# Crear BD y usuario
sudo -u postgres psql -c "CREATE USER awsacademy WITH PASSWORD 'AWsAcademy2026!';"
sudo -u postgres psql -c "CREATE DATABASE awsacademydb OWNER awsacademy;"
```

**Prueba de conectividad (EVIDENCIA REAL):**

```bash
# Desde APP01 (10.10.11.119):
psql -h 10.10.20.125 -U awsacademy -d awsacademydb -c "SELECT version();"
# → PostgreSQL 15.19 on x86_64-amazon-linux-gnu

INSERT INTO connectivity_test (app_instance) VALUES ('APP01');
# → INSERT 0 1

# Desde APP02 (10.10.12.82):
INSERT INTO connectivity_test (app_instance) VALUES ('APP02');
# → INSERT 0 1

SELECT * FROM connectivity_test;
#  id | app_instance |         test_time
# ----+--------------+----------------------------
#   1 | APP01        | 2026-09-17 22:52:23
#   2 | APP02        | 2026-09-17 22:52:53
```

✅ **Conectividad bidireccional confirmada.** Ambas instancias de app pueden leer y escribir en PostgreSQL.

### 4.6 FASE 5 — S3 y CloudWatch

```bash
# Bucket S3 para backups
aws s3 mb s3://awsacademy-backup-1789674826 --region us-east-1

# Alarma CloudWatch — 5XX del ALB
aws cloudwatch put-metric-alarm \
  --alarm-name AWsAcademy-ALB-5XX \
  --metric-name HTTPCode_Target_5XX_Count \
  --namespace AWS/ApplicationELB \
  --statistic Sum --period 60 --evaluation-periods 2 --threshold 0 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:669186512136:RedshiftSNS

# Alarma CloudWatch — CPU alta del ASG
aws cloudwatch put-metric-alarm \
  --alarm-name AWsAcademy-HighCPU \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average --period 120 --evaluation-periods 2 --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:669186512136:RedshiftSNS
```

> Ambas alarmas notifican al topic SNS `RedshiftSNS` que ya existía en la cuenta Academy.

### 4.7 FASE 6 — Tailscale (conexión multicloud)

```bash
# Instalación vía SSM Run Command en las 3 EC2:
aws ssm send-command \
  --document-name AWS-RunShellScript \
  --targets Key=instanceids,Values=$INSTANCE_ID \
  --parameters commands='curl -fsSL https://tailscale.com/install.sh | sh'
```

**Estado:** ✅ Instalado en APP01, APP02 y DB.  
**Pendiente:** `tailscale up` — requiere **auth key** del panel de administración de Tailscale (`tailscale.com/admin`). Sin la key, Tailscale no se autentica.

---

## 5. AZURE — ESTADO Y POR QUÉ NO SE USÓ

### 5.1 Estado actual

| Componente | Estado |
|---|---|
| Azure CLI (`az`) | ⚠️ Instalado vía pipx pero **ROTO** |
| Perfil Azure | ✅ Existe `~/.azure/azureProfile.json` — sesión previa de `az login` |
| Suscripción | `66da5b2c-dd50-4403-b701-0d468b9c50d8` — "Azure subscription 1" |
| Usuario | `glender.samuel06@gmail.com` |
| Tenant | `2ea8bb1d-490b-4319-8de2-5d41cb513989` — "Default Directory" |
| Recursos desplegados | ❌ NINGUNO |

### 5.2 Error que impide usar `az`

```text
OSError: [Errno 30] Read-only file system: '/home/glender/.azure/az.sess'
```

**Causa:** el filesystem raíz está montado `ro`. `az` intenta escribir su archivo de sesión en `~/.azure/az.sess` y falla.

### 5.3 Cómo conectar Azure en este entorno (para otro agente)

**Opción A — Bypass del archivo de sesión:**
```bash
# Intentar sin cache de sesión
AZURE_CONFIG_DIR=/tmp/azure-tmp az login
```
Esto redirige `~/.azure` a `/tmp` que sí es escribible. Pero la sesión no persiste.

**Opción B — Service Principal (recomendada para agentes):**
```bash
# Sin archivos locales, usando solo variables de entorno:
export AZURE_CLIENT_ID="..."
export AZURE_TENANT_ID="2ea8bb1d-490b-4319-8de2-5d41cb513989"
export AZURE_CLIENT_SECRET="..."
az account show  # debería funcionar sin escribir ~/.azure/
```

**Opción C — Montar el workspace como `rw` en `~/.azure`:**
```bash
# Si el sandbox lo permite:
ln -sf /home/glender/Proyectos/AWsacademy/.azure /home/glender/.azure
mkdir -p /home/glender/Proyectos/AWsacademy/.azure
```

> ⚠️ Ninguna de estas opciones fue probada en esta sesión. Quedan como guía para el próximo agente.

### 5.4 Plan de Azure (no ejecutado)

Según la plantilla del proyecto (`plantilla.docx`), la arquitectura incluía:

- VNet `10.20.0.0/16`
- 2 subnets (una pública, una de base de datos)
- NAT Gateway
- VM con aplicación y base de datos (Azure VM + Azure Blob Storage)
- Conexión **AWS ↔ Azure vía Tailscale** (en lugar de VPN site-to-site)

Nada de esto se desplegó. El plan era conectar ambas nubes a través de Tailscale una vez que las VMs de Azure estuvieran corriendo.

---

## 6. ORACLE CLOUD INFRASTRUCTURE (OCI) — ESTADO Y POR QUÉ NO SE USÓ

### 6.1 Estado actual

| Componente | Estado |
|---|---|
| OCI CLI | ❌ **NO INSTALADO** |
| `oci` | Comando no encontrado |

### 6.2 Cómo instalar OCI CLI en Debian

```bash
# Instalación rápida:
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# O vía pip (más ligero):
python3 -m pip install oci-cli

# Configurar:
oci setup config
# Pide: OCID de usuario, OCID de tenant, región, fingerprint de clave API
```

### 6.3 Requisitos previos no cumplidos

Para usar OCI se necesita:

1. Cuenta de Oracle Cloud (Free Tier o de pago)
2. Generar clave API RSA (2048+ bits): `openssl genrsa -out ~/.oci/oci_api_key.pem 2048`
3. Subir la clave pública en la consola OCI (Identity → Users → API Keys)
4. Conocer el OCID del compartment

> **Nada de esto se configuró. OCI está completamente vacío.**

### 6.4 Por qué no se usó OCI

La plantilla mencionaba OCI, pero el enfoque real del proyecto fue solo AWS + Azure. OCI quedó como mención teórica. Si se desea habilitar, el procedimiento es el de arriba.

---

## 7. LIMITACIONES DE AWS ACADEMY ENCONTRADAS (TABLA DE ERRORES)

| Acción intentada | API | Resultado | Workaround aplicado |
|---|---|---|---|
| Crear rol IAM | `iam:CreateRole` | ❌ AccessDenied | Usar `LabInstanceProfile` existente |
| Crear RDS | `rds:CreateDBInstance` | ❌ AccessDenied | PostgreSQL en EC2 |
| `aws login` | — | ❌ No funciona | Credenciales temporales manuales |
| Consola AWS | — | ❌ Sin acceso | Solo CLI/SDK |
| `export-credentials` | STS | ⚠️ A veces devuelve el mismo token | Stop Lab + Start Lab |
| Listener ALB | ELBv2 | ⚠️ Se pierde al reiniciar lab | `start-lab.sh` automático |
| Bloqueo `voc-cancel-cred` | Varias APIs | ⚠️ Aparece tras reinicio | Esperar / renovar lab |
| Credenciales expiran | STS | ⏳ ~30-45 min | Renovación manual continua |
| `az` no escribe sesión | — | ❌ `OSError: [Errno 30] ROFS` | `AZURE_CONFIG_DIR=/tmp` o Service Principal |

---

## 8. ARCHIVOS DEL PROYECTO

| Archivo | Función |
|---|---|
| `DESARROLLO-CLOUD-COMPUTING.md` | 📘 **Este documento** — guía completa para agentes |
| `deploy-infra.sh` | Automatiza creación de VPC, subnets, IGW, NAT, route tables, SGs |
| `deploy-ec2.sh` | Automatiza Launch Template y Auto Scaling Group |
| `db-user-data.sh` | Script de instalación y configuración de PostgreSQL 15 |
| `user-data.sh` | User-data de las EC2 de aplicación (Apache + página HTML) |
| `infra-params.env` | ⭐ IDs de todos los recursos — referencia para scripts |
| `AWsAcademy-Key.pem` | 🔑 Key pair SSH para las 3 EC2 (`chmod 400`) |
| `ec2-trust-policy.json` | Política de confianza EC2 (no aplicó por falta de permisos IAM) |
| `start-lab.sh` | ⭐ Script de arranque automático tras reinicio del lab |
| `plantilla.docx` | Plantilla oficial del proyecto integrador (Word) |

---

## 9. RUNBOOK — RECUPERACIÓN TRAS REINICIO DEL LAB

### 9.1 El problema

Cuando el lab de AWS Academy expira (~4 horas):

| Recurso | ¿Sobrevive? |
|---|---|
| VPC, subnets, IGW, NAT GW | ✅ Sí |
| EC2 | ⚠️ Se apagan (stop). El ASG lanza reemplazos automáticamente |
| ALB + Target Group | ✅ Sí, pero el **listener se pierde** |
| S3 | ✅ Sí |
| PostgreSQL (datos) | ✅ En disco EBS de la EC2 de DB |
| Key Pair | ✅ Persiste localmente |

### 9.2 Procedimiento de arranque con `start-lab.sh`

```bash
# PASO 1 — Obtener credenciales frescas en Vocareum
aws configure export-credentials --format env

# PASO 2 — Editar start-lab.sh con las 3 líneas de credenciales
nano start-lab.sh
# Reemplazar PEGAR_AQUI con access_key_id, secret_access_key, session_token

# PASO 3 — Ejecutar
cd /home/glender/Proyectos/AWsacademy
./start-lab.sh
```

**Qué hace el script automáticamente:**

1. ✅ Verifica credenciales (`aws sts get-caller-identity`)
2. ✅ Reactiva el ASG si `DesiredCapacity` está en 0
3. ✅ Espera hasta que 2 instancias estén `running` (máx. 180s)
4. ✅ Recrea el listener del ALB (siempre se pierde)
5. ✅ Registra las instancias en el Target Group
6. ✅ Espera 30s y verifica health checks
7. ✅ Muestra la URL pública lista para usar

### 9.3 ¿Qué NO hace el script?

- No renueva credenciales por ti → hay que pegarlas manualmente
- No recrea la VPC ni recursos base → esos persisten
- No reinstala PostgreSQL → los datos sobreviven en el disco EBS
- No configura Tailscale (`tailscale up` pendiente)

---

## 10. CHECKLIST PARA UN NUEVO AGENTE

Si otro agente (o tú mismo en una sesión nueva) retoma este proyecto, este es el orden:

1. **[ ] Verificar entorno**
   - `pwd` → debe estar en `/home/glender/Proyectos/AWsacademy`
   - `aws --version` → `aws-cli/2.36.47`
   - `az version` → probablemente roto — ver sección 5.2
   - ¿`/` sigue montado `ro`? → `mount | grep ' / '`

2. **[ ] Credenciales AWS**
   - Obtener de Vocareum: `aws configure export-credentials --format env`
   - Verificar: `AWS_PROFILE=academy aws sts get-caller-identity`
   - Si `ExpiredToken` o `InvalidClientTokenId`: renovar en Vocareum

3. **[ ] Levantar infraestructura**
   - Ejecutar `./start-lab.sh` (con credenciales actualizadas)
   - Verificar: `curl http://AWsAcademy-ALB-1953310462.us-east-1.elb.amazonaws.com`
   - Debe devolver HTML con `<h1>APP0X - AWsAcademy</h1>`

4. **[ ] Probar conectividad BD**
   - `ssh -i AWsAcademy-Key.pem ec2-user@10.10.11.119`
   - `psql -h 10.10.20.125 -U awsacademy -d awsacademydb -c "SELECT version();"`

5. **[ ] Azure (si se requiere)**
   - Intentar `AZURE_CONFIG_DIR=/tmp/azure-tmp az login`
   - O usar Service Principal con variables de entorno
   - Desplegar VNet `10.20.0.0/16` + VM + Blob Storage

6. **[ ] Tailscale**
   - Generar auth key en `tailscale.com/admin`
   - `tailscale up --auth-key=<KEY>` en las 3 EC2
   - Probar conectividad entre AWS y Azure vía Tailscale IPs (`100.x.x.x`)

7. **[ ] OCI (si se requiere)**
   - Instalar OCI CLI: `python3 -m pip install oci-cli`
   - Configurar: `oci setup config`

---

## 11. RESUMEN DE HERRAMIENTAS CLI USADAS

| CLI | Comando principal | Propósito |
|---|---|---|
| **aws** | `aws ec2`, `aws elbv2`, `aws autoscaling`, `aws s3`, `aws cloudwatch`, `aws ssm`, `aws sts`, `aws configure agent-toolkit` | TODO el despliegue AWS |
| **aws configure** | `aws configure set`, `aws configure agent-toolkit` | Configuración de perfil e instalación de Agent Toolkit |
| **uvx** | `uvx mcp-proxy-for-aws@latest ...` | Ejecutar el MCP Server de AWS |
| **az** | `az login`, `az account show`, `az vm create` | Azure CLI (**roto en este entorno**) |
| **psql** | `psql -h ... -U ... -d ...` | Pruebas de conectividad a PostgreSQL |
| **ssh** | `ssh -i AWsAcademy-Key.pem ec2-user@...` | Acceso a las EC2 |
| **jq** | `aws ... --query '...'` procesado con `jq` | Filtrado de JSON |
| **curl** | `curl http://ALB-DNS` | Pruebas HTTP al balanceador |
| **chmod** | `chmod 400 AWsAcademy-Key.pem` | Proteger la key pair |

---

*Documento generado el 24 Septiembre 2026 — AWsAcademy — Glender Vargas*
